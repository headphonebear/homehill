# Orchard – Installation and Bootstrap

This document describes the installation of the Orchard cluster, from the initial setup of the three NucBox G3 machines with Alpine Linux to the first successful `kubectl get pods -A` from the desktop.

Orchard consists of a single K3s Control Plane Node (`apple`) and two Worker Nodes (`lemon`, `plum`).

All steps are documented in such a way that a rebuild (e.g., after hardware replacement or reinstallation) is possible reproducibly.

---

## 1. Goal and Overview

Goal of this installation:

-   Setup of a small but fully-fledged Kubernetes cluster based on K3s.
-   Use of three identical NucBox G3 as physical nodes.
-   Access to the cluster from a separate desktop computer (`bearcube`) via `kubectl`.
-   Preparation for later GitOps (Argo CD) and Ingress/TLS configuration (Traefik + Let's Encrypt).

Core decisions:

-   **K3s** instead of "Full" Kubernetes (kubeadm) to save resources on the NUCs.
-   **Alpine Linux** as a minimalist, fast base OS.
-   A **single Control Plane Node** (completely sufficient for Homelab).
-   K3s Default components (Traefik, CoreDNS, local-path-provisioner, metrics-server) are used and not disabled.

---

## 2. Hardware and Roles

All three Orchard nodes are based on the same hardware:

-   Model: NucBox G3
-   Role in the cluster:
    -   `apple` – Control Plane / Master
    -   `lemon` – Worker
    -   `plum` – Worker

The concrete hardware specification (CPU, RAM, SSD size, specifics) is recorded in a separate document:

-   `k8s/orchard/setup/hardware-specs.md` (TODO)

---

## 3. Installing Alpine Linux on the NucBox G3

Each of the three nodes receives a fresh Alpine installation. The steps are basically identical, differences only exist in Hostname and IP/Network.

### 3.1. Boot from Alpine Installation Medium

1.  Download Alpine Linux (Extended) ISO.
2.  Create bootable USB stick.
3.  Boot NucBox G3 from USB.
4.  Select the standard option in the Alpine Boot Menu (Extended variant).

### 3.2. Basic Installation

On every node:

-   Log in as `root` (no password).
-   Start the interactive installer:

    ```sh
    setup-alpine
    ```

-   Important decisions during `setup-alpine`:
    -   Keyboard layout, Timezone, Locale → suitable for Homehill.
    -   Hostname:
        -   `apple`
        -   `lemon`
        -   `plum`
    -   Network:
        -   Either static IPs in the Homehill network
        -   or DHCP, as long as the IPs are reliable or fixed via DHCP reservation.
    -   SSH Server: Install and activate `openssh`.
    -   Disk Layout:
        -   Usual partitioning (root + possibly separate EFI/Boot).
        -   Install Alpine on the internal SSD.

After completion:

-   Remove USB stick.
-   Reboot.
-   Log in via SSH from another host (or continue working directly on the console).

---

## 4. Basic Configuration on all Nodes

On each of the three nodes:

### 4.1. Update and Install Basic Packages

```sh
apk update
apk upgrade
apk add htop curl nano
```

Optional: Time synchronization and small comfort settings (e.g., `chrony`, alias for `kubectl`, etc.). The minimum is sufficient for the bootstrap.

### 4.2. Check Network and DNS

Ensure that:

-   Internet access is available (`ping 1.1.1.1`, `ping github.com`).
-   Name resolution for `*.homehill.de` works (if already set up).
-   The nodes can ping each other (`ping apple`, `ping lemon`, `ping plum`), provided DNS entries exist.

---

## 5. Install K3s Server on `apple`

`apple` is the Control Plane Node (K3s Server).

### 5.1. K3s via the Official Install Script

On `apple` as `root`:

```sh
curl -sfL https://get.k3s.io | sh -
```

Important points:

-   The script:
    -   finds the current "stable" K3s version,
    -   downloads the matching binary,
    -   verifies the hash,
    -   installs `k3s` under `/usr/local/bin`,
    -   sets up the `k3s` service and starts it.

Note:
With very slow downloads from GitHub, downloading the binary can take some time, even if your own internet connection is fast.

### 5.2. First Check of the K3s Server

After successful installation:

```sh
k3s kubectl get nodes
```

should display the node `apple` as `Ready` with role `control-plane,master`, e.g.:

```text
NAME    STATUS   ROLES                  AGE   VERSION
apple   Ready    control-plane,master   2m    v1.33.6+k3s1
```

### 5.3. Read Node Token for Worker Nodes

To allow `lemon` and `plum` to join the cluster as workers, the `node-token` from the server is required:

```sh
cat /var/lib/rancher/k3s/server/node-token
```

Securely copy the output token – it will be used on the worker nodes as `K3S_TOKEN`.

---

## 6. Install K3s Agent on `lemon` and `plum`

On `lemon` and `plum`, K3s is installed as an Agent (Worker Node). Both connect to the API Server on `apple`.

### 6.1. K3s Agent with K3S_URL and K3S_TOKEN

On `lemon` as `root`:

```sh
curl -sfL https://get.k3s.io | \
  K3S_URL="https://192.168.x.y:6443" \
  K3S_TOKEN="INSERT_TOKEN_FROM_APPLE_HERE" \
  sh -
```

On `plum` analogously:

```sh
curl -sfL https://get.k3s.io | \
  K3S_URL="https://192.168.x.y:6443" \
  K3S_TOKEN="INSERT_TOKEN_FROM_APPLE_HERE" \
  sh -
```

Note:
During the initial bootstrap, the **IP address** of the API server is used (`https://192.168.x.y:6443`), since no valid TLS certificate is configured for `apple.homehill.de` yet.

Both are possible in principle; in the long term, the FQDN with a matching certificate is desirable.

### 6.2. Check from the Server

Back on `apple` (or from the desktop with `kubectl`):

```sh
k3s kubectl get nodes
```

Expected output:

```text
NAME    STATUS   ROLES                  AGE   VERSION
apple   Ready    control-plane,master   45m   v1.33.6+k3s1
lemon   Ready    <none>                 14m   v1.33.6+k3s1
plum    Ready    <none>                 15m   v1.33.6+k3s1
```

The cluster is now complete from K3s's perspective: one Control Plane, two Worker Nodes.

---

## 7. Setup kubectl on the Desktop

Daily access to the cluster takes place from a desktop computer (e.g., `bearcube`) on which `kubectl` is installed.

### 7.1. Install kubectl

Under Linux (Ubuntu-based), the official Kubernetes documentation is recommended:

1.  Install `kubectl` following the instructions at
    https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
2.  Ensure that `kubectl` is in the `PATH`:

    ```sh
    kubectl version --client
    ```

### 7.2. Copy kubeconfig from `apple`

On `apple`, the K3s kubeconfig is normally located at:

```text
/etc/rancher/k3s/k3s.yaml
```

This file is copied to the desktop, e.g.:

```sh
# on apple
scp /etc/rancher/k3s/k3s.yaml user@bearcube:/home/user/.kube/config
```

(Create folder `~/.kube` on `bearcube` beforehand if necessary.)

### 7.3. Adjust Server Address

The `k3s.yaml` generated by K3s uses `https://127.0.0.1:6443` as the API endpoint by default. On the desktop, this address must be adjusted to the IP of `apple`:

```yaml
server: https://192.168.x.y:6443
```

(Later, when TLS/Ingress is correct, this can be switched to an FQDN.)

### 7.4. Rename Context: `default` → `orchard`

The kubeconfig provided by K3s often uses `default` everywhere as the name for:

-   Cluster
-   Context
-   User
-   `current-context`

For better readability and clarity, everything is switched to `orchard`. With `sed`:

```sh
sed -i 's/name: default/name: orchard/g' ~/.kube/config
sed -i 's/cluster: default/cluster: orchard/g' ~/.kube/config
sed -i 's/user: default/user: orchard/g' ~/.kube/config
sed -i 's/current-context: default/current-context: orchard/g' ~/.kube/config
```

Then check:

```sh
kubectl config current-context
# expected: orchard
```

---

## 8. First Cluster Checks

With set up `kubectl` and active `orchard` context:

### 8.1. Nodes

```sh
kubectl get nodes
```

Expected output (Example):

```text
NAME    STATUS   ROLES                  AGE   VERSION
apple   Ready    control-plane,master   45m   v1.33.6+k3s1
lemon   Ready    <none>                 14m   v1.33.6+k3s1
plum    Ready    <none>                 15m   v1.33.6+k3s1
```

### 8.2. System Pods

```sh
kubectl get pods -A
```

Typical output immediately after installation:

```text
NAMESPACE     NAME                                      READY   STATUS      RESTARTS   AGE
kube-system   coredns-6d668d687-8swbm                   1/1     Running     0          50m
kube-system   helm-install-traefik-65f9n                0/1     Completed   1          50m
kube-system   helm-install-traefik-crd-nh54t            0/1     Completed   0          50m
kube-system   local-path-provisioner-869c44bfbd-vjwbp   1/1     Running     0          50m
kube-system   metrics-server-7bfffcd44-6j7p8            1/1     Running     0          50m
kube-system   svclb-traefik-7a9db005-8k7hm              2/2     Running     0          50m
kube-system   svclb-traefik-7a9db005-jg7vx              2/2     Running     0          20m
kube-system   svclb-traefik-7a9db005-r4g4x              2/2     Running     0          20m
kube-system   traefik-865bd56545-xfp82                  1/1     Running     0          50m
```

The cluster is thus functional and ready for further configuration (Ingress/TLS, Namespaces, GitOps, etc.).

---

## 9. Known Limitations and Open Points

At the time of this installation, the following points are intentionally still open or provisional:

1.  **FQDN and TLS for the API Server**
    -   Currently, the API server is addressed via an internal IP.
    -   Planned is the use of an FQDN like `apple.homehill.de` or `orchard-api.homehill.de` with a valid TLS certificate.
    -   For this, either K3s itself or an upstream reverse proxy (Traefik with Let's Encrypt certificate) will be used.

2.  **Ingress and Public Services**
    -   Traefik is already active as Ingress Controller, but not yet configured for productive IngressRoutes.
    -   Planned:
        -   DNS-01 Challenge via Hetzner DNS for Let's Encrypt certificates.
        -   Use of `*.homehill.de` for the services in the cluster.

3.  **GitOps / Argo CD**
    -   The Orchard cluster is not yet connected to Argo CD.
    -   The repository (`homehill`) is being prepared to later:
        -   Define namespaces, basic infrastructure, and workloads declaratively.
        -   Roll out changes via Git commits.

4.  **Security & RBAC**
    -   Currently, the cluster runs without a fine-grained RBAC model.
    -   Goal is to map the existing Homehill identity schema:
        -   System Users, Service Goblins, AI Identities
        -   Namespaces, ServiceAccounts, Roles, and RoleBindings.

---

## 10. Summary

With these steps, Orchard is successfully installed as a three-node K3s cluster:

-   Three Alpine-based NucBox G3 nodes (`apple`, `lemon`, `plum`).
-   K3s Server on `apple`, Agents on `lemon` and `plum`.
-   Access via `kubectl` from desktop, context `orchard`.
-   All K3s Core components run stably and ready for further configuration.

The next steps (separate documents):

-   `k8s/orchard/README.md` → Overview of the cluster and its role in Homehill.
-   `k8s/orchard/setup/network.md` → Network details (IPs, DNS, Pi-hole, Hetzner).
-   `docs/GITOPS-SETUP.md` → Design and structure of the GitOps pipeline with Argo CD.

Orchard is thus the Kubernetes heart of Homehill – ready to be filled with life. 🌳💚

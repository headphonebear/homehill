# Orchard Cluster Bootstrap

This document describes how to bootstrap the **Orchard** Kubernetes cluster from scratch using **k3s**.

**Cluster Information:**
- **Name:** `orchard`
- **Nodes:** `apple` (control plane), `lemon` (worker), `plum` (worker)
- **Distribution:** k3s (lightweight Kubernetes)
- **Git Repository:** `https://github.com/headphonebear/homehill` (public repo)
- **Branch:** `new_season`
- **Path Prefix:** `homehill/clusters/`

---

## Prerequisites

- All nodes (`apple`, `lemon`, `plum`) are running Alpine Linux.
- SSH access to all nodes with root privileges.
- Local machine has `kubectl` and `helm` installed.
- Git clone of the `homehill` repository on branch `new_season`.

---

## Bootstrap Steps

### 1. Initialize the k3s Control Plane

SSH into the control plane node `apple`:

```shell
ssh root@apple
```

Install k3s on the control plane node **without the built-in Traefik** (we will install our own later):

```shell
curl -sfL https://get.k3s.io | sh -s - server \
  --disable traefik \
  --write-kubeconfig-mode 644 \
  --flannel-backend=vxlan
```

> **Note:** The `--disable traefik` flag prevents k3s from deploying its built-in Traefik ingress controller, as we will manage Traefik via ArgoCD.

Wait for k3s to start. Verify the control plane is ready:

```shell
k3s kubectl get nodes
```

Get the node token for joining worker nodes:

```shell
cat /var/lib/rancher/k3s/server/node-token
```

Copy this token for use in the next step.

Get the control plane IP address (usually the node's main IP, e.g., `192.168.x.x` or internal hostname).

Exit the SSH session.

---

### 2. Join Worker Nodes

For each worker node (`lemon`, `plum`), SSH into the node and install k3s in agent mode:

```shell
ssh root@lemon
```

Install k3s agent, replacing `<CONTROL_PLANE_IP>` with the IP/hostname of `apple` and `<NODE_TOKEN>` with the token from step 1:

```shell
curl -sfL https://get.k3s.io | K3S_URL=https://<CONTROL_PLANE_IP>:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -
```

Exit the SSH session. Repeat for `plum`.

Verify all nodes are ready:

```shell
kubectl get nodes
```

---

### 3. Copy kubeconfig to Local Machine

From your local machine, copy the kubeconfig from `apple`:

```shell
scp root@apple:/etc/rancher/k3s/k3s.yaml ~/.kube/orchard-config
```

Edit `~/.kube/orchard-config` and replace `127.0.0.1` with the actual IP or hostname of `apple`.

Set the KUBECONFIG environment variable (or merge into your existing `~/.kube/config`):

```shell
export KUBECONFIG=~/.kube/orchard-config
```

Verify connectivity:

```shell
kubectl get nodes
```

---

### 4. Prepare ArgoCD Namespace

Create the `argocd` namespace:

```shell
kubectl create namespace argocd
```

> **Note:** No Git credentials secret is needed because the homehill repository is public. ArgoCD will clone via HTTPS without authentication.

---

### 5. Install ArgoCD with Helm

Add the ArgoCD Helm repository:

```shell
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
```

Download Helm dependencies for the ArgoCD umbrella chart:

```shell
cd homehill/clusters/apps/argocd/orchard
helm dependency update
cd -
```

Install ArgoCD from the local Helm chart:

```shell
helm install argocd ./homehill/clusters/apps/argocd/orchard \
  --namespace argocd \
  --values ./homehill/clusters/apps/argocd/orchard/values.yaml \
  --wait \
  --timeout 5m
```

---

### 6. Apply ArgoCD Application Manifests

Apply the App-of-Apps and individual `Application` manifests so ArgoCD takes over cluster management:

```shell
kubectl apply -f ./homehill/clusters/argocd/orchard/
```

---

### 7. Access ArgoCD UI

Get the initial admin password:

```shell
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Port-forward to the ArgoCD server:

```shell
kubectl -n argocd port-forward service/argocd-server 8080:80
```

Open your browser to `http://localhost:8080` and log in with username `admin` and the password from above.

---

## Next Steps

- Verify that all ArgoCD Applications are synced.
- Check the status of infrastructure components (Traefik, cert-manager, storage, monitoring, sealed-secrets).
- Review logs and troubleshoot any failing pods.
- Once Traefik is deployed, configure an IngressRoute for ArgoCD at `argocd.orchard.homehill.de`.

---

## Notes

- **k3s Built-in Components:** We disabled Traefik at install time to manage it via ArgoCD/Helm instead. Flannel CNI is enabled by default and does not need separate installation.
- **Public Repository:** The homehill repo is public, so no SSH keys or tokens are needed for ArgoCD to sync.
- All paths are relative to the root of the `homehill` repository.
- This bootstrap process is idempotent: re-running steps (except initial k3s server install) should be safe.
- k3s automatically manages node tokens and certificate rotation.

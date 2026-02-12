# 🌳 Orchard – Homehill Kubernetes Cluster

Orchard is the Kubernetes cluster in the Homehill homelab.
It is gradually replacing parts of the previous Docker Swarm environment with K3s-based orchestration, while remaining closely integrated into the existing Homehill architecture.

**Goal of Orchard:**

-   **Platform** for central Homelab services (Nextcloud, Immich, Keycloak, Monitoring, Slack Bridge, AI Tools, etc.).
-   **GitOps-friendly foundation** (Argo CD) to manage configurations in a reproducible and version-controlled manner.
-   **Clean separation** between "old" Swarm stacks and "new" Kubernetes workloads.

---

## 🧱 Cluster Overview

**Distribution:** K3s (Lightweight Kubernetes)
**Version:** v1.33.6+k3s1
**Control Plane:** Single-node control plane on `apple`
**Worker Nodes:** `lemon`, `plum`
**Cluster Name (kubectl context):** `orchard`

### Nodes

The three Orchard nodes run on identical NucBox G3 hardware (Alpine Linux):

-   `apple` – Control Plane / Master
-   `lemon` – Worker
-   `plum` – Worker

(The original Swarm nodes `nook`, `greenhouse`, `dovecote`, and other devices like NAS and Desktop are documented in the Homehill inventory and remain as the infrastructure backbone.)

---

## 🧩 Packaged Components (K3s Defaults)

Immediately after the K3s installation, only the components included with K3s are running in the cluster:

-   **CoreDNS** – DNS service for the cluster.
-   **Traefik** – Ingress Controller & Reverse Proxy (K3s Deployment).
-   **local-path-provisioner** – StorageClass for simple local PersistentVolumes.
-   **metrics-server** – Resource metrics for `kubectl top` & HPA.
-   **svclb Pods for Traefik** – LoadBalancer implementation via DaemonSet (one pod per node).

Check directly after bootstrap:

```bash
kubectl get nodes
kubectl get pods -A
```

---

## 🌐 Network & Access

-   **API Server:**
    Currently accessible internally via IP (e.g., `https://192.168.x.y:6443`).
    Planned: FQDN such as `apple.homehill.de` or `orchard-api.homehill.de` with a valid TLS certificate.
-   **kubectl Access:**
    `kubectl` is installed on the desktop (`bearcube`); the `kubeconfig` was copied from `apple` and adapted to the internal IP of the API server.
    The active context is named:

    ```bash
    kubectl config current-context
    # orchard
    ```

-   **DNS / External Domains:**
    The existing Homehill DNS infrastructure (`*.homehill.de` via Pi-hole and Hetzner DNS) will later be used for Ingress routes.
    Goal: Traefik + Let's Encrypt (DNS-01 Challenge via Hetzner) for wildcard certificates.

---

## 👥 Identity & Security (Homehill Schema)

Orchard follows the existing Homehill UID/GID and role schema (System Users, Bear Identities, Service Goblins, AI Assistants).
In the long term, this model will be transferred to Kubernetes, including:

-   Namespaces according to Roles / Projects.
-   ServiceAccounts and RBAC that map "Service Goblins".
-   Separation between **Content Owner** (e.g., `mk3`, `coder`) and **Service Runner** (technical accounts / ServiceAccounts).
-   Own identities for AI Assistants (e.g., Ana) for access to cluster APIs.

Currently, the cluster is in **Bootstrap State** without fine-grained RBAC configuration; this will follow with the first productive workloads.

---

## 📌 Current Status

-   K3s v1.33.6 is installed on all three nodes.
-   `apple` acts as the Control Plane, `lemon` and `plum` are successful Worker Nodes.
-   `kubectl` is set up on the desktop, context `orchard` is active.
-   All K3s Core components are running (`coredns`, `traefik`, `local-path-provisioner`, `metrics-server`, `svclb-traefik`).
-   No productive workloads yet; Orchard is ready for the first "real" deployments.

---

## 🚧 Next Steps

1.  **TLS & Ingress**
    -   Configure Traefik for:
        -   Let's Encrypt certificates (DNS-01 Challenge via Hetzner DNS API).
        -   Clean hosts like `*.homehill.de` for Kubernetes services.
    -   Possibly switch to cert-manager later if required.

2.  **GitOps / Argo CD**
    -   Set up `k8s/orchard/gitops/`:
        -   `base/` for namespaces, basic infrastructure (Monitoring, Ingress, Storage, Logging).
        -   `argo-apps/` for App-of-Apps pattern.
    -   Deploy Argo CD in the cluster and wire it to this repository.

3.  **Workload Migration & New Services**
    -   Bring planned projects (Nextcloud, Immich, Jellyfin successor, Keycloak, Uptime Kuma, etc.) to Orchard step-by-step.
    -   Gradually migrate services from the Swarm world, **only** if they are being touched anyway ("Never stop a running system").

4.  **Monitoring & Runbooks**
    -   Establish Kubernetes monitoring (e.g., Netdata/Grafana/Prometheus) for Orchard.
    -   Add runbooks for common tasks and incident response.

---

## 📂 Further Documentation

-   `k8s/orchard/setup/INSTALLATION.md`
    Detailed step-by-step guide: From NucBox G3 installation (Alpine Linux) to the first successful `kubectl get pods -A`.

-   `docs/ARCHITECTURE.md`
    General overview of Homehill: Swarm Cluster, Orchard Cluster, NAS, Pi-hole, Network Topology.

-   `docs/GITOPS-SETUP.md`
    Design and implementation of the GitOps pipeline (Argo CD, Repos, Branching Strategy).

---

*Orchard is the Kubernetes heart of Homehill – grown from late nights, trip-hop beats, and a lot of attention to detail.* 🌳💚
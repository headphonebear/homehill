# Orchard – Network Configuration

This document describes the network architecture of the Orchard cluster as well as its integration into the existing Homehill infrastructure.

---

## 1. Network Overview

Orchard uses the existing Homehill network and integrates seamlessly into the established infrastructure:

-   **Network Segment**: Homehill LAN (`192.168.x.0/24` or similar)
-   **DNS Service**: Existing (Pi-hole for local resolution)
-   **External Domain**: `homehill.de` (registered, DNS at Hetzner)
-   **Planned Wildcard**: `*.homehill.de` for Ingress Services

---

## 2. Orchard Nodes – IP Addressing

### 2.1. Static IPs or DHCP Reservation

All three Orchard nodes should have **reliable, consistent IP addresses**:

| Hostname | Role | IP Address | MAC Address | Note |
| :--- | :--- | :--- | :--- | :--- |
| `apple` | Control Plane | `192.168.x.y` | `xx:xx:xx:xx:xx:xx` | Via DHCP reservation or static |
| `lemon` | Worker | `192.168.x.z` | `yy:yy:yy:yy:yy:yy` | Via DHCP reservation or static |
| `plum` | Worker | `192.168.x.w` | `zz:zz:zz:zz:zz:zz` | Via DHCP reservation or static |

**Recommendation**: DHCP reservation is easier to maintain than static configuration per node.
(Configuration in the home network router or DHCP server, e.g., Pi-hole.)

### 2.2. DNS Names for Nodes

If not already present, DNS entries for the nodes should exist in the local network:

```text
apple.homehill.de    → 192.168.x.y
lemon.homehill.de    → 192.168.x.z
plum.homehill.de     → 192.168.x.w
```

These are resolved via the local DNS server (Pi-hole).
**Important**: This later also enables `K3S_URL="https://apple.homehill.de:6443"` instead of just IP-based.

---

## 3. Kubernetes API Server Access

### 3.1. Current State (Bootstrap)

During the initial installation, the **IP address** of the API server is used:

```yaml
# ~/.kube/config
server: https://192.168.x.y:6443
```

This is functional, but:
-   Access breaks if IPs change (e.g., after restart with DHCP).
-   For Production / GitOps, a stable FQDN with TLS certificate is better.

### 3.2. Goal: FQDN + TLS for Kubernetes API

In the long term, the API server should be accessible via a **stable FQDN** with a **valid TLS certificate**.

Options:

**Option A: K3s itself with cert-manager**
-   K3s can be configured via the installation with `--tls-san=apple.homehill.de`.
-   Then needs a certificate (via Let's Encrypt, self-signed, etc.).

**Option B: Reverse Proxy in front of K3s**
-   A reverse proxy (e.g., Traefik or nginx) outside the cluster sits in front of the API server.
-   This proxy terminates TLS with a valid certificate.

**Option C: Hetzner DNS + Traefik (later, when GitOps is running)**
-   After Argo CD Setup: IngressRoute with Let's Encrypt DNS-01 Challenge.
-   This is the long-term, maintenance-friendly model.

**Current**: We leave it at **Option A (simple)** – K3s with certificate, or wait for Traefik integration.

---

## 4. Traefik Ingress Controller (K3s Default)

K3s comes with Traefik by default.
Traefik runs as a **Deployment** in the `kube-system` namespace:

```bash
kubectl get deploy -n kube-system traefik
```

### 4.1. Traefik Service and LoadBalancer

Traefik is configured as a **Service** of type `LoadBalancer`:

```bash
kubectl get svc -n kube-system traefik
```

Output (Example):

```text
NAME      TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
traefik   LoadBalancer   10.43.x.x       192.168.x.y   80:30080/TCP,443:30443/TCP   50m
```

**EXTERNAL-IP**: This is the IP of the node where Traefik is running (or a Floating IP with multiple nodes).

### 4.2. DaemonSet svclb-traefik

K3s uses its own **Service Load Balancer (svclb)** to implement the Traefik service.
An `svclb-traefik-*` pod runs on every node:

```bash
kubectl get pods -n kube-system | grep svclb-traefik
```

These pods ensure that incoming traffic on port 80/443 is routed to Traefik.

---

## 5. Ingress Routes for Services

### 5.1. Principle

To make a service in the cluster accessible via `*.homehill.de`:

1.  Define **IngressRoute** (or Ingress resource).
2.  Specify Host Name (e.g., `navidrome.homehill.de`).
3.  TLS Certificate (automatically via Let's Encrypt or manual).
4.  Traffic is forwarded from Traefik to the service.

Example (future):

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: navidrome
  namespace: default
spec:
  entryPoints:
    - web
    - websecure
  routes:
    - match: Host(`navidrome.homehill.de`)
      kind: Rule
      services:
        - name: navidrome
          port: 6595
  tls:
    certResolver: letsencrypt
    domains:
      - main: homehill.de
        sans:
          - '*.homehill.de'
```

### 5.2. TLS / Let's Encrypt Integration (TODO)

Currently, this is **not yet configured**.
Planned integration of:

-   **Let's Encrypt** (free certificates)
-   **Hetzner DNS API** (for DNS-01 Challenge)
-   **Traefik CertResolver** (automatic renewal)

This is described in separate documentation: `docs/GITOPS-SETUP.md` or `k8s/orchard/setup/traefik-letsencrypt.md` (TODO).

---

## 6. Network Isolation and Segmentation

### 6.1. Kubernetes Internal Network

K3s uses by default:

-   **Service CIDR**: `10.43.0.0/16` (Internal Cluster Services)
-   **Pod CIDR**: `10.42.0.0/16` (Pod IPs)

These are connected via the Kubernetes network plugin (Flannel in K3s).

### 6.2. Namespace Segregation (later)

In the long term, Homehill structure will be mapped via namespaces:

-   `default` – for Test/Development
-   `homelab-apps` – productive services
-   `monitoring` – Prometheus, Grafana, etc.
-   `system` – Cluster System Components (already `kube-system`, `kube-public`)

RBAC policies per namespace later as well.

---

## 7. DNS Resolution in the Cluster

### 7.1. CoreDNS

The Cluster DNS Service runs as a **Deployment** in the `kube-system` namespace:

```bash
kubectl get deploy -n kube-system coredns
```

CoreDNS resolves:

-   **Intra-Cluster Services**: `service-name.namespace.svc.cluster.local`
-   **External Domains**: (forward to external resolvers, e.g., 1.1.1.1)

### 7.2. Service Discovery

A pod can reach another service via:

```
http://service-name.namespace.svc.cluster.local:port
```

Example:

```bash
# Inside the cluster
curl http://navidrome.default.svc.cluster.local:6595
```

---

## 8. Network Policies (future)

Currently, **no NetworkPolicies** are defined.
This means: Every pod can communicate with every other pod.

In the future, NetworkPolicies can be introduced to:

-   Isolate services from each other.
-   Allow only necessary communication.
-   Increase security in the cluster.

Example Pattern:

-   `monitoring` namespace may scrape metrics from all.
-   `homelab-apps` may communicate with each other.
-   External communication only on port 80/443 (HTTP/HTTPS).

---

## 9. Firewall and External Access

### 9.1. Home Network Firewall

The cluster is by default **only accessible in the local home network**.

-   K3s API Server: only accessible from `bearcube` (Desktop).
-   Traefik Ingress (Port 80/443): only accessible from local devices.

### 9.2. External Access (not recommended)

If services should later be accessible via the Internet:

-   Set up port forwarding in the home router (e.g., Port 443 → `192.168.x.y:443`).
-   Then: FQDN must be resolved externally (e.g., DynDNS with Hetzner).
-   TLS is then **critical** (Let's Encrypt with DNS-01).

**Recommendation for Homelab**: Stay local, external access via VPN.

---

## 10. Monitoring and Troubleshooting

### 10.1. Network Debugging in the Cluster

```bash
# See Pods and their IPs
kubectl get pods -A -o wide

# Service IPs
kubectl get svc -A

# Endpoints (where is a service actually running?)
kubectl get endpoints -A

# Network Policies (if present)
kubectl get networkpolicies -A

# DNS Test (in container)
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
# In container:
nslookup kubernetes.default
nslookup google.com
```

### 10.2. Common Network Problems

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Pod cannot reach Service | DNS not resolved | `kubectl logs -n kube-system deploy/coredns` |
| Ingress Route not working | Traefik not ready | `kubectl get pods -n kube-system traefik-*` |
| External Domain not accessible | no TLS certificate | Let's Encrypt + Traefik Setup (TODO) |
| IP address changes after reboot | DHCP reservation not active | Set up DHCP reservation for Node MACs |

---

## 11. Summary of Network Architecture

```
┌─────────────────────────────────────────┐
│       Homehill LAN (192.168.x.0/24)     │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  Orchard K3s Cluster             │   │
│  │                                  │   │
│  │  apple (Control Plane)           │   │
│  │  lemon (Worker)                  │   │
│  │  plum (Worker)                   │   │
│  │                                  │   │
│  │  Traefik (Ingress Controller)    │   │
│  │  CoreDNS (Cluster DNS)           │   │
│  │  Local-Path-Provisioner (Storage)│   │
│  └──────────────────────────────────┘   │
│                                         │
│  Pi-hole DNS (local resolution)         │
│                                         │
│  Hetzner DNS (external, homehill.de)    │
└─────────────────────────────────────────┘
```

---

## 12. Next Steps

1.  **Set up DHCP Reservations** for `apple`, `lemon`, `plum`.
2.  **Configure DNS Entries** for `*.homehill.de` at Hetzner.
3.  **Configure Traefik + Let's Encrypt** (separate doc).
4.  **Deploy First IngressRoute** (e.g., for Dashboard or Test Service).
5.  **NetworkPolicies** later, when production services are running.

---

*Orchard grows – from physical hardware via network to the virtual service world.* 🌳💚
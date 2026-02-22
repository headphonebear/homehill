# 🏡 Homehill Clusters - GitOps Repository

**Production Kubernetes clusters managed with ArgoCD + GitOps**

This repository contains the complete configuration for Homehill's Kubernetes infrastructure. Everything is version-controlled, auditable, and reproducible.

---

## 🚀 Quick Start - For the Impatient

### Access Grafana (Monitoring)

```bash
# Get admin password
kubectl get secret -n monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d && echo

# Port-forward to local machine
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80

# Open: http://localhost:3000
# Login: admin / <password from above>
```

### Access ArgoCD UI

```bash
# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo

# Port-forward
kubectl port-forward -n argocd svc/argocd-server 8080:443

# Open: https://localhost:8080
# Login: admin / <password from above>
```

### Sync an Application Manually

```bash
# When selfHeal is disabled, apps need manual sync
argocd app sync <app-name>

# Examples:
argocd app sync monitoring
argocd app sync longhorn
argocd app sync traefik
```

---

## 🏗️ What's Running Here

### Active Cluster: **Orchard** 🍎

**Nodes:**
- `apple` (control-plane) - HP EliteDesk 800 G2
- `plum` (worker) - HP EliteDesk 800 G2  
- `peach` (worker) - HP EliteDesk 800 G2

**Core Stack:**

| Component | Purpose | Namespace | Status |
|-----------|---------|-----------|--------|
| **k3s** | Kubernetes distribution | system | ✅ |
| **ArgoCD** | GitOps controller | `argocd` | ✅ |
| **Longhorn** | Distributed block storage | `longhorn-system` | ✅ |
| **Traefik** | Ingress controller + TLS | `traefik` | ✅ |
| **cert-manager** | Let's Encrypt automation | `cert-manager` | ✅ |
| **Sealed Secrets** | Encrypted secrets in Git | `kube-system` | ✅ |
| **Monitoring Stack** | Prometheus + Grafana + VictoriaMetrics | `monitoring` | ✅ |

**Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│  Internet → Hetzner DNS → Let's Encrypt (DNS01)             │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
                     ┌──────────────┐
                     │   Traefik    │  (Ingress, TLS termination)
                     └──────┬───────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
   ┌─────────┐       ┌──────────┐       ┌──────────┐
   │ Grafana │       │  ArgoCD  │       │   Apps   │
   └─────────┘       └──────────┘       └──────────┘
        │                                      │
        ↓                                      ↓
   ┌──────────────────────────────────────────────┐
   │          Longhorn (HA Storage)               │
   │  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
   │  │  apple  │  │  plum   │  │  peach  │     │
   │  └─────────┘  └─────────┘  └─────────┘     │
   └──────────────────────────────────────────────┘
```

---

## 📂 Repository Structure

```
clusters/
├── argocd/
│   └── orchard/           # ArgoCD Application manifests
│       ├── longhorn.yaml  # Defines Longhorn app
│       ├── monitoring.yaml # Defines monitoring stack
│       └── ...            # One file per app
│
├── apps/
│   ├── longhorn/
│   │   └── orchard/
│   │       └── values.yaml  # Helm values for Longhorn
│   ├── monitoring/
│   │   └── orchard/
│   │       └── values.yaml  # Monitoring stack config
│   └── ...                  # One directory per app
│
├── docs/
│   ├── TROUBLESHOOTING.md   # Common problems & fixes
│   └── SECRETS.md           # SealedSecrets workflow
│
└── README.md                # This file
```

**How GitOps Works Here:**

1. **You** commit changes to `clusters/apps/<app>/orchard/values.yaml`
2. **ArgoCD** detects the change (polls every 3 minutes)
3. **ArgoCD** syncs the app (if `selfHeal: true`, or manually)
4. **Kubernetes** applies the new config
5. **Profit!** 🎉

---

## 🔧 Common Tasks

### Add a New Application

1. **Create Helm values:** `clusters/apps/<app-name>/orchard/values.yaml`
2. **Create ArgoCD Application:** `clusters/argocd/orchard/<app-name>.yaml`
3. **Commit & push**
4. **ArgoCD auto-detects** the new Application manifest
5. **Sync manually** (first time): `argocd app sync <app-name>`

### Update an Application

1. **Edit values:** `clusters/apps/<app-name>/orchard/values.yaml`
2. **Commit & push**
3. **If selfHeal is enabled:** ArgoCD syncs automatically
4. **If selfHeal is disabled:** `argocd app sync <app-name>`

### Check Application Status

```bash
# List all apps
argocd app list

# Detailed status
argocd app get <app-name>

# Diff between Git and cluster
argocd app diff <app-name>
```

---

## 🎯 Why selfHeal is Disabled for Some Apps

**Apps with `selfHeal: false`:**
- `monitoring` (Grafana uses ReadWriteOnce PVC)

**Why?**

Grafana has a single PVC that can't be shared between pods. If ArgoCD auto-syncs every time the Grafana Secret drifts (random password regeneration), it creates a new ReplicaSet, triggering a Multi-Attach error.

**Solution:** Manual sync when you actually want to update.

**Apps with `selfHeal: true`:**
- Stateless apps (Traefik, ArgoCD itself)
- Apps with ReadWriteMany storage

---

## 🔐 Secrets Management

We use **Sealed Secrets** to store encrypted secrets in Git.

**TL;DR:**
```bash
# Create a secret
kubectl create secret generic my-secret --from-literal=key=value --dry-run=client -o yaml | \
  kubeseal -o yaml > my-secret-sealed.yaml

# Commit the sealed secret
git add my-secret-sealed.yaml
git commit -m "add: my-secret"
git push
```

**Full guide:** [SECRETS.md](docs/SECRETS.md)

---

## 🚨 Troubleshooting

**Common issues:**

| Problem | Quick Fix | Full Guide |
|---------|-----------|------------|
| Multi-Attach error for Grafana PVC | `kubectl delete pod <old-pod> --force` | [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#multi-attach-errors) |
| ArgoCD shows "Progressing" forever | Check pod logs, look for failing containers | [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#stuck-deployments) |
| Webhook TLS errors in operator logs | Webhooks disabled in values.yaml | [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#webhook-tls-errors) |
| Let's Encrypt cert not issued | Check cert-manager logs, DNS propagation | [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#certificate-issues) |

**Full troubleshooting guide:** [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📊 Monitoring & Dashboards

**Grafana is the primary UI** for cluster metrics.

**Recommended Dashboards to Import:**

1. **15759** - Kubernetes Views / Global (cluster overview)
2. **15760** - Kubernetes Views / Namespaces (per-namespace resources)
3. **15761** - Kubernetes Views / Pods (detailed pod metrics)
4. **13032** - Longhorn Overview ⚠️ **CRITICAL** (storage health)
5. **7249** - Traefik 2.x (ingress metrics)
6. **10229** - VictoriaMetrics Single (VM performance)

**How to import:**
1. Go to Grafana → Dashboards → Import
2. Enter dashboard ID (e.g., `13032`)
3. Select Prometheus data source
4. Click Import

---

## 🚀 Bootstrap from Scratch

**"My cluster exploded. How do I rebuild?"**

1. **Install k3s** on all nodes
2. **Install ArgoCD:** `kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml`
3. **Add this repo to ArgoCD:** Point ArgoCD to `https://github.com/headphonebear/homehill.git`
4. **Sync app-of-apps:** ArgoCD deploys everything from Git
5. **Wait 5-10 minutes** for Longhorn, monitoring, etc. to come up
6. **Verify:** `kubectl get pods -A`

**Detailed bootstrap guide:** Coming soon! (TODO)

---

## 📚 Additional Documentation

- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Battle-tested fixes for common problems
- **[SECRETS.md](docs/SECRETS.md)** - Complete SealedSecrets workflow
- **[Architecture Overview](docs/orchard/ARCHITECTURE.md)** - Deep dive into cluster design
- **[UID/GID Schema](../homehill_uid_schema.md)** - Homehill user/service ID allocations

---

## 🦊 About This Repo

**Owner:** Headphonebear  
**Cluster:** Orchard (Production)  
**Philosophy:** Everything in Git. No manual kubectl apply. If it's not in the repo, it doesn't exist.  

**Contributing:** This is a personal homelab, but feel free to steal ideas! 💚

---

**Happy GitOps-ing!** 🎉🦊💪

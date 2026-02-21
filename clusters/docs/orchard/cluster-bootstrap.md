# 🍎 Orchard Cluster Bootstrap

This document describes how to bootstrap the **Orchard** Kubernetes cluster from scratch using **k3s**.

## 🎯 Cluster Information

| Property | Value |
|----------|-------|
| **Name** | `orchard` 🍎🍋🍑 |
| **Control Plane** | `apple.homehill.de` (192.168.1.50) 🍎 |
| **Worker Nodes** | `lemon.homehill.de` (192.168.1.51) 🍋<br>`plum.homehill.de` (192.168.1.52) 🍑 |
| **Distribution** | k3s (lightweight Kubernetes) |
| **Git Repository** | `https://github.com/headphonebear/homehill` (public) |
| **Branch** | `new_season` |
| **Path Prefix** | `clusters/` |

---

## ✅ Prerequisites

Before starting the bootstrap process, ensure:

- ✅ All nodes (`apple.homehill.de`, `lemon.homehill.de`, `plum.homehill.de`) are running **Alpine Linux**
- ✅ SSH access to all nodes with **root privileges**
- ✅ Local machine has `kubectl` and `helm` installed
- ✅ Git clone of the `homehill` repository on branch `new_season`
- ✅ Network connectivity between all nodes (192.168.1.50-52 can reach each other)
- ✅ **If re-bootstrapping:** Sealed Secrets keys (`sealing-key.key` + `sealing-key.crt`) backed up and ready

---

## 🚀 Bootstrap Steps

### Step 0: Clean Existing Cluster (if applicable) 🧹

> **⚠️ WARNING:** This will **completely destroy** the existing cluster and all its data!

If re-bootstrapping or if a previous k3s installation exists, clean it up first.

#### Clean Worker Nodes First

```bash
ssh root@lemon.homehill.de
/usr/local/bin/k3s-agent-uninstall.sh
exit

ssh root@plum.homehill.de
/usr/local/bin/k3s-agent-uninstall.sh
exit
```

> **WHY:** Cleaning workers first gracefully drains workloads before control plane shutdown.

#### Clean Control Plane Node

```bash
ssh root@apple.homehill.de
/usr/local/bin/k3s-uninstall.sh
exit
```

> **Note:** Control plane uses `k3s-uninstall.sh`, workers use `k3s-agent-uninstall.sh`.

#### Cleanup Longhorn Volumes (if needed)

On each node:

```bash
rm -rf /mnt/longhorn/*
```


#### Verify Cleanup

On each node:

```bash
which k3s                        # Should return nothing
ls -la /var/lib/rancher/k3s/     # Should return "No such file or directory"
ps aux | grep k3s                # Should only show the grep command itself
ls -la /mnt/longhorn/            # Should be empty when starting over fresh
```

---

### Step 1: Initialize the k3s Control Plane 🍎

SSH into the control plane node:

```bash
ssh root@apple.homehill.de
```

Install k3s:

```bash
curl -sfL https://get.k3s.io | sh -s - server \
  --disable traefik \
  --write-kubeconfig-mode 644 \
  --flannel-backend=vxlan
```

> **WHY flags:**
> - `--disable traefik`: We manage Traefik via ArgoCD with custom config
> - `--write-kubeconfig-mode 644`: Makes kubeconfig readable by non-root users
> - `--flannel-backend=vxlan`: Explicit default for documentation clarity

Verify control plane is ready:

```bash
k3s kubectl get nodes
# Expected: apple with status Ready
```

Get the **node token** for joining workers:

```bash
cat /var/lib/rancher/k3s/server/node-token
```

**Copy this token!** It looks like: `K10abcdef1234567890::server:1234567890abcdef1234567890abcdef`

Exit:

```bash
exit
```

---

### Step 2: Join Worker Nodes 🍋🍑

Replace `<NODE_TOKEN>` with the token from Step 1.

#### Join lemon 🍋

```bash
ssh root@lemon.homehill.de

curl -sfL https://get.k3s.io | K3S_URL=https://apple.homehill.de:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -

exit
```

#### Join plum 🍑

```bash
ssh root@plum.homehill.de

curl -sfL https://get.k3s.io | K3S_URL=https://apple.homehill.de:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -

exit
```

#### Verify All Nodes Are Ready

From apple (still in SSH):

```bash
k3s kubectl get nodes
```

Expected output:

```
NAME     STATUS   ROLES                  AGE   VERSION
apple    Ready    control-plane,master   5m    v1.34.x+k3s1
lemon    Ready    <none>                 2m    v1.34.x+k3s1
plum     Ready    <none>                 1m    v1.34.x+k3s1
```

---

### Step 3: Copy kubeconfig to Local Machine 💻

From your **local machine**:

```bash
scp root@apple.homehill.de:/etc/rancher/k3s/k3s.yaml ~/.kube/orchard-config
```

Edit `~/.kube/orchard-config` and replace `127.0.0.1` with `192.168.1.50` (FQDN apple.homehill.de does not work at this stage because no TLS is set up yet)

```bash
sed -i 's/127.0.0.1/apple.homehill.de/g' ~/.kube/orchard-config
# Or manually: nano ~/.kube/orchard-config
```

Set the KUBECONFIG environment variable:

```bash
export KUBECONFIG=~/.kube/orchard-config
```

> **TIP:** Make it permanent: `echo 'export KUBECONFIG=~/.kube/orchard-config' >> ~/.bashrc`

Verify connectivity:

```bash
kubectl get nodes
# Should show apple, lemon, plum all Ready
```

---

### Step 4: Prepare ArgoCD Namespace 📦

Create the `argocd` namespace:

```bash
kubectl create namespace argocd
```

### Step 4.5: Label nodes for Longhorn

Label nodes for Longhorn disk config:
```bash
kubectl label nodes apple lemon plum \
  node.longhorn.io/create-default-disk=config
```

Annotate disk path:
```bash
kubectl annotate nodes apple lemon plum \
  'node.longhorn.io/default-disks-config=[{"path":"/mnt/longhorn","allowScheduling":true}]'
```

Verify:
```bash
kubectl get nodes --show-labels | grep longhorn
```

> **Note:** No Git credentials needed - `homehill` is a public repository.

---

### Step 5: Install ArgoCD with Helm 🚢

Add ArgoCD Helm repository:

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
```

Navigate to homehill repository:

```bash
cd ~/homehill
```

Download Helm dependencies:

```bash
cd clusters/apps/argocd/orchard
helm dependency update
cd ~/homehill
```

Install ArgoCD:

```bash
helm install argocd ./clusters/apps/argocd/orchard \
  --namespace argocd \
  --values ./clusters/apps/argocd/orchard/values.yaml \
  --wait \
  --timeout 5m
```

Verify ArgoCD is running:

```bash
kubectl get pods -n argocd
# All pods should show Running or Completed
```

---

### Step 5.5: Install Sealed Secrets Key (Re-bootstrap Only) 🔐

> **⚠️ CRITICAL STEP FOR RE-BOOTSTRAP:** If you have existing SealedSecrets in Git, you **must** install your backed-up private key **before** deploying applications. Otherwise, all encrypted secrets will fail to decrypt!

**Skip this step if:** This is a fresh installation with no existing SealedSecrets in Git. The sealed-secrets controller will generate new keys automatically when deployed in Step 6.

#### Install Your Backed-Up Keys

Replace `/path/to/` with the actual path to your backed-up keys:

```bash
# Create the sealed-secrets namespace (controller will be deployed here)
kubectl create namespace kube-system --dry-run=client -o yaml | kubectl apply -f -

# Install the private key (using your backup)
kubectl create secret tls sealed-secrets-key \
  --cert=/path/to/sealing-key.crt \
  --key=/path/to/sealing-key.key \
  -n kube-system \
  --dry-run=client -o yaml | kubectl apply -f -

# Label the secret so the controller recognizes it
kubectl label secret sealed-secrets-key \
  -n kube-system \
  sealedsecrets.bitnami.com/sealed-secrets-key=active \
  --overwrite
```

> **WHY:** Installing the key **before** the controller starts prevents it from generating a new key. When the controller starts in Step 6, it will find and use your existing key.

Verify the key is installed:

```bash
kubectl get secret sealed-secrets-key -n kube-system
# Should show the secret exists
```

---

### Step 6: Deploy Applications via ArgoCD 📋

Apply the **App-of-Apps** pattern to let ArgoCD manage the cluster:

```bash
kubectl apply -f ./clusters/argocd/orchard/
```

Check ArgoCD Applications:

```bash
kubectl get applications -n argocd
```

Expected output (applications will be syncing):

```
NAME                          SYNC STATUS   HEALTH STATUS
app-of-apps                   Synced        Healthy
argocd                        Synced        Healthy
cert-manager                  Synced        Progressing
cert-manager-webhook-hetzner  Synced        Progressing
sealed-secrets                Synced        Healthy
storage                       Synced        Healthy
traefik                       Synced        Progressing
...
```

> **App-of-Apps Pattern:** ArgoCD watches `clusters/argocd/orchard/` and automatically deploys all Application manifests, creating a full GitOps workflow.

---

### Step 7: Access ArgoCD UI 🖥️

Get the initial admin password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
echo
```

Port-forward to ArgoCD:

```bash
kubectl -n argocd port-forward service/argocd-server 8080:80
```

Open browser to **http://localhost:8080** and log in:
- **Username:** `admin`
- **Password:** (from command above)

You should see the ArgoCD dashboard with all applications! 🎉

---

## ✅ Post-Bootstrap Verification

Run these checks to ensure everything is healthy:

```bash
# Check all applications are synced
kubectl get applications -n argocd

# Check infrastructure pods
kubectl get pods -n traefik
kubectl get pods -n cert-manager
kubectl get pods -n kube-system | grep sealed-secrets

# Monitor certificate issuance
kubectl get certificate -A
kubectl get clusterissuer

# Check Hetzner DNS webhook
kubectl get pods -n cert-manager -l app.kubernetes.io/name=cert-manager-webhook-hetzner
```

Once Traefik and certificates are ready, ArgoCD will be accessible at: `https://argocd.orchard.homehill.de`

Stop the port-forward (Ctrl+C) and use the HTTPS URL instead.

---

## 🎯 Next Steps

### For Fresh Installations: Backup Sealed Secrets Keys

If you skipped Step 5.5 (fresh install), the sealed-secrets controller generated new keys. **Back them up now:**

```bash
# Wait for sealed-secrets to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=sealed-secrets -n kube-system --timeout=300s

# Extract keys
kubectl get secret -n kube-system -l sealedsecrets.bitnami.com/sealed-secrets-key -o yaml > sealed-secrets-backup.yaml

# Also save as individual files
kubectl get secret sealed-secrets-key -n kube-system -o jsonpath='{.data.tls\.crt}' | base64 -d > sealing-key.crt
kubectl get secret sealed-secrets-key -n kube-system -o jsonpath='{.data.tls\.key}' | base64 -d > sealing-key.key
```

**⚠️ CRITICAL:** Store these files securely:
- Password manager (1Password, Bitwarden)
- Encrypted USB drive
- Secure notes app (Obsidian with encryption)

Without these keys, you cannot re-bootstrap the cluster and decrypt existing SealedSecrets!

### Change ArgoCD Admin Password

```bash
argocd account update-password
```

### Ongoing GitOps Management

- All changes go through Git commits to `new_season` branch
- ArgoCD auto-syncs applications with `syncPolicy.automated`
- Manual sync via ArgoCD UI or CLI when needed

---

## 📝 Notes

- **Traefik:** Disabled in k3s, managed via ArgoCD
- **Flannel CNI:** Included by default (VXLAN backend)
- **CoreDNS, ServiceLB, Local Path Provisioner:** All included in k3s
- **DNS:** Nodes use FQDN (`apple.homehill.de` etc.) via Pi-hole or `/etc/hosts`
- **Public Repo:** No SSH keys needed, ArgoCD clones via HTTPS
- **Idempotency:** Re-running most steps is safe except k3s control plane install (resets cluster!)

---

## 🐛 Troubleshooting

### Worker Nodes Won't Join

```bash
# From worker node - check API reachability
curl -k https://apple.homehill.de:6443
# Should return JSON (forbidden error is OK)

# Check DNS resolution
nslookup apple.homehill.de
# Should return 192.168.1.50
```

### ArgoCD Applications Stuck "Progressing"

```bash
# Check pod events
kubectl describe pod <pod-name> -n <namespace>

# Check node resources
kubectl top nodes
```

### Certificates Not Issuing

```bash
# Check certificate status
kubectl describe certificate <cert-name> -n <namespace>

# Check challenges
kubectl get challenges -A

# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager -f

# Check webhook logs
kubectl logs -n cert-manager -l app.kubernetes.io/name=cert-manager-webhook-hetzner -f
```

Common issues:
- Hetzner API token invalid/expired
- DNS propagation delay (wait 2-3 min)
- Webhook not running

### SealedSecrets Cannot Decrypt

```bash
# Check active key
kubectl get secret -n kube-system sealed-secrets-key -o yaml

# Compare fingerprint with backup
openssl x509 -in sealing-key.crt -noout -fingerprint
```

If wrong key installed: Install correct key from backup and restart controller:

```bash
kubectl rollout restart deployment sealed-secrets -n kube-system
```

---

## 🦊 Credits

**Documentation by:** Ana 🦊 (Coding with Ana Space)  
**Cluster Design:** Headphonebear 🐻 & Ana 🦊  
**Updated:** February 15, 2026  
**Location:** Kiel, Germany 🇩🇪  

---

**Built with ❤️, Club Mate 🍵, and binary algebra ✨**

*"Never Stop Running" - homehill philosophy*

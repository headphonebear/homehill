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

---

## 🚀 Bootstrap Steps

### Step 0: Clean Existing Cluster (if applicable) 🧹

If you're re-bootstrapping the cluster or have a previous k3s installation, clean it up first.

> **⚠️ WARNING:** This will **completely destroy** the existing cluster and all its data. Make sure you have backups of any important data or SealedSecrets keys!

#### Clean Worker Nodes First

Start with the worker nodes to gracefully drain workloads:

```bash
# SSH to lemon
ssh root@lemon.homehill.de
/usr/local/bin/k3s-agent-uninstall.sh
exit

# SSH to plum
ssh root@plum.homehill.de
/usr/local/bin/k3s-agent-uninstall.sh
exit
```

> **WHY: Worker nodes first**  
> Cleaning worker nodes before the control plane ensures workloads are gracefully drained and don't cause errors when the control plane shuts down.

#### Clean Control Plane Node

```bash
# SSH to apple
ssh root@apple.homehill.de
/usr/local/bin/k3s-uninstall.sh
exit
```

> **WHY: Different uninstall scripts**  
> Control plane nodes use `k3s-uninstall.sh` while worker nodes use `k3s-agent-uninstall.sh`. The scripts are automatically created during k3s installation.

#### Verify Cleanup

On each node, verify k3s is completely removed:

```bash
# Check if k3s binary is gone
which k3s
# Should return nothing (command not found)

# Check if data directory is gone
ls -la /var/lib/rancher/k3s/
# Should return "No such file or directory"

# Check no k3s processes are running
ps aux | grep k3s
# Should only show the grep command itself
```

> **Note:** If the uninstall scripts don't exist, the cluster was likely never fully installed or already cleaned. Proceed to Step 1.

---

### Step 1: Initialize the k3s Control Plane 🍎

SSH into the control plane node **apple.homehill.de**:

```bash
ssh root@apple.homehill.de
# WHY: apple.homehill.de (192.168.1.50) is the control plane node
# Using FQDN ensures DNS resolution works consistently
```

Install k3s on the control plane node **without the built-in Traefik**:

```bash
curl -sfL https://get.k3s.io | sh -s - server \
  --disable traefik \
  --write-kubeconfig-mode 644 \
  --flannel-backend=vxlan
```

> **WHY: `--disable traefik`**  
> We disable the built-in Traefik because we manage our own Traefik via ArgoCD with custom configuration (TLS, middlewares, IngressRoutes). The k3s bundled Traefik is too basic for our needs.

> **WHY: `--write-kubeconfig-mode 644`**  
> Makes the kubeconfig readable by non-root users. Default is 600 (root only). This allows easier access for debugging and avoids permission issues when copying the kubeconfig.

> **WHY: `--flannel-backend=vxlan`**  
> VXLAN is the default Flannel backend and works well in most networks. We explicitly set it for documentation clarity. Alternative backends (host-gw, wireguard) exist but VXLAN is the safest choice for mixed environments.

Wait for k3s to start (usually takes 30-60 seconds). Verify the control plane is ready:

```bash
k3s kubectl get nodes
# Expected output: apple with status Ready
```

Get the **node token** for joining worker nodes:

```bash
cat /var/lib/rancher/k3s/server/node-token
```

**Copy this token!** You'll need it in Step 2. The token looks like:

```
K10abcdef1234567890::server:1234567890abcdef1234567890abcdef
```

> **WHY: Node Token**  
> The node token is a shared secret that authenticates worker nodes when joining the cluster. It's generated during control plane initialization and stored in `/var/lib/rancher/k3s/server/node-token`. Without this token, worker nodes cannot join.

Exit the SSH session:

```bash
exit
```

---

### Step 2: Join Worker Nodes 🍋🍑

For each worker node, SSH in and install k3s in **agent mode**.

#### Join lemon.homehill.de 🍋

```bash
ssh root@lemon.homehill.de
```

Install k3s agent, replacing `<NODE_TOKEN>` with the token from Step 1:

```bash
curl -sfL https://get.k3s.io | K3S_URL=https://apple.homehill.de:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -
```

> **WHY: `K3S_URL=https://apple.homehill.de:6443`**  
> This tells the worker node where to find the control plane API server. Port 6443 is the standard Kubernetes API port. We use the FQDN (apple.homehill.de) instead of IP for DNS-based resolution.

> **WHY: `K3S_TOKEN`**  
> This is the shared secret from Step 1 that authenticates this node as part of the Orchard cluster.

Exit the SSH session:

```bash
exit
```

#### Join plum.homehill.de 🍑

Repeat the same process for **plum**:

```bash
ssh root@plum.homehill.de

curl -sfL https://get.k3s.io | K3S_URL=https://apple.homehill.de:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -

exit
```

#### Verify All Nodes Are Ready

From your local machine (after Step 3), verify all nodes joined successfully:

```bash
kubectl get nodes
```

Expected output:

```
NAME                    STATUS   ROLES                  AGE     VERSION
apple.homehill.de       Ready    control-plane,master   5m      v1.28.x+k3s1
lemon.homehill.de       Ready    <none>                 2m      v1.28.x+k3s1
plum.homehill.de        Ready    <none>                 1m      v1.28.x+k3s1
```

---

### Step 3: Copy kubeconfig to Local Machine 💻

From your **local machine**, copy the kubeconfig from **apple.homehill.de**:

```bash
scp root@apple.homehill.de:/etc/rancher/k3s/k3s.yaml ~/.kube/orchard-config
```

> **WHY: Separate kubeconfig file**  
> We use `orchard-config` instead of overwriting `~/.kube/config` to keep clusters separate. You can manage multiple clusters by switching KUBECONFIG environment variable.

Edit `~/.kube/orchard-config` and replace `127.0.0.1` with the actual IP or FQDN of **apple**:

```bash
# Open the file in your editor
nano ~/.kube/orchard-config

# Find this line:
    server: https://127.0.0.1:6443

# Replace with:
    server: https://apple.homehill.de:6443
# OR if DNS doesn't work:
    server: https://192.168.1.50:6443
```

> **WHY: Replace 127.0.0.1**  
> The default kubeconfig uses `127.0.0.1` which only works from within the control plane node itself. We need to use the actual IP (192.168.1.50) or FQDN (apple.homehill.de) to access the cluster from our local machine.

Set the KUBECONFIG environment variable:

```bash
export KUBECONFIG=~/.kube/orchard-config
```

> **TIP:** Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent:
> ```bash
> echo 'export KUBECONFIG=~/.kube/orchard-config' >> ~/.bashrc
> ```

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

> **WHY: Manual namespace creation**  
> While ArgoCD can create its own namespace, we create it explicitly first to avoid race conditions during Helm install. This also allows us to pre-populate namespace with labels or secrets if needed.

> **Note:** No Git credentials secret is needed because the `homehill` repository is **public**. ArgoCD will clone via HTTPS without authentication.

---

### Step 5: Install ArgoCD with Helm 🚢

Add the ArgoCD Helm repository:

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
```

> **WHY: Official ArgoCD Helm repo**  
> We use the official ArgoCD Helm charts maintained by the Argo Project. This ensures we get stable, tested releases.

Navigate to the homehill repository (adjust path as needed):

```bash
cd ~/homehill
```

Download Helm dependencies for the ArgoCD umbrella chart:

```bash
cd clusters/apps/argocd/orchard
helm dependency update
cd ~/homehill
```

> **WHY: `helm dependency update`**  
> Our ArgoCD Chart.yaml references the official ArgoCD chart as a dependency. This command downloads it into `charts/` directory so Helm can install it.

Install ArgoCD from the local Helm chart:

```bash
helm install argocd ./clusters/apps/argocd/orchard \
  --namespace argocd \
  --values ./clusters/apps/argocd/orchard/values.yaml \
  --wait \
  --timeout 5m
```

> **WHY: `--wait --timeout 5m`**  
> Helm waits for all ArgoCD pods to be ready before returning. Timeout of 5 minutes is sufficient for initial deployment. If it times out, ArgoCD might still be starting - check with `kubectl get pods -n argocd`.

Wait for all ArgoCD components to be ready:

```bash
kubectl get pods -n argocd
# All pods should show Running or Completed status
```

---

### Step 6: Apply ArgoCD Application Manifests 📋

Apply the **App-of-Apps** and individual `Application` manifests so ArgoCD takes over cluster management:

```bash
kubectl apply -f ./clusters/argocd/orchard/
```

> **WHY: App-of-Apps Pattern**  
> The `app-of-apps.yaml` tells ArgoCD to watch the `clusters/argocd/orchard/` directory and automatically deploy all Application manifests it finds. This creates a GitOps workflow where:
> 1. You commit a new `foo.yaml` Application manifest to Git
> 2. ArgoCD detects the change and deploys the `foo` application
> 3. All infrastructure is managed declaratively via Git

Wait a few seconds, then check ArgoCD Applications:

```bash
kubectl get applications -n argocd
```

Expected output (applications may still be syncing):

```
NAME                              SYNC STATUS   HEALTH STATUS
app-of-apps                       Synced        Healthy
argocd                            Synced        Healthy
cert-manager                      Synced        Progressing
cert-manager-webhook-hetzner      Synced        Progressing
sealed-secrets                    Synced        Healthy
storage                           Synced        Healthy
traefik                           Synced        Progressing
...
```

---

### Step 7: Access ArgoCD UI 🖥️

Get the initial admin password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
echo  # Add newline for readability
```

> **WHY: Initial admin secret**  
> ArgoCD generates a random admin password on first install and stores it in this secret. After first login, you should change the password or configure SSO.

Port-forward to the ArgoCD server:

```bash
kubectl -n argocd port-forward service/argocd-server 8080:80
```

> **WHY: Port-forward**  
> Initially, ArgoCD is only accessible inside the cluster. Port-forwarding creates a tunnel from your local machine (localhost:8080) to the ArgoCD service. Later, we'll expose ArgoCD via Traefik IngressRoute at `argocd.orchard.homehill.de`.

Open your browser to **http://localhost:8080** and log in with:
- **Username:** `admin`
- **Password:** (from command above)

You should see the ArgoCD dashboard with all your applications! 🎉

---

## 🎯 Next Steps

### Install Sealed Secrets Private Key 🔐

Sealed Secrets encrypts your Kubernetes secrets so they can be safely stored in Git. The encryption uses a public/private key pair.

#### Understanding Sealed Secrets Keys

- **Public Key (`sealing-key.crt`):** Used to encrypt secrets. Can be shared safely.
- **Private Key (`sealing-key.key`):** Used by the sealed-secrets controller to decrypt secrets in-cluster. **Must be kept secret!**

> **WHY: Re-use existing keys**  
> If you're re-bootstrapping the cluster, you **must** install your existing Sealed Secrets private key. Otherwise, all your existing SealedSecret manifests in Git cannot be decrypted and your applications will fail to start.

#### If You Have Existing Keys (Re-bootstrap Scenario)

If you saved your keys from a previous cluster installation, install them now:

```bash
# Copy your backed-up keys to the cluster
kubectl create secret tls sealed-secrets-key \
  --cert=/path/to/sealing-key.crt \
  --key=/path/to/sealing-key.key \
  -n sealed-secrets

# Label the secret so sealed-secrets controller uses it
kubectl label secret sealed-secrets-key \
  -n sealed-secrets \
  sealedsecrets.bitnami.com/sealed-secrets-key=active

# Restart the sealed-secrets controller to pick up the key
kubectl rollout restart deployment sealed-secrets-controller -n sealed-secrets
```

> **⚠️ CRITICAL:** Without your original private key, you cannot decrypt existing SealedSecrets! Always backup these keys:
> - Store in password manager (1Password, Bitwarden, etc.)
> - Keep offline backup on encrypted USB drive
> - Store in secure note-taking app (Obsidian with encryption, etc.)

#### If You Don't Have Keys (Fresh Installation)

If this is a brand new cluster and you don't have SealedSecrets in Git yet:

```bash
# Wait for sealed-secrets controller to generate keys automatically
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=sealed-secrets -n sealed-secrets --timeout=300s

# Extract and backup the generated keys
kubectl get secret -n sealed-secrets sealed-secrets-key -o jsonpath='{.data.tls\.crt}' | base64 -d > sealing-key.crt
kubectl get secret -n sealed-secrets sealed-secrets-key -o jsonpath='{.data.tls\.key}' | base64 -d > sealing-key.key

# ⚠️ BACKUP THESE FILES NOW!
echo "🔐 Sealed Secrets keys saved to:"
echo "  - sealing-key.crt (public key)"
echo "  - sealing-key.key (private key - KEEP SECRET!)"
```

#### Get Public Key for Sealing Secrets

To encrypt new secrets locally, you need the public key:

```bash
# Fetch public key from the cluster
kubeseal --fetch-cert --controller-name=sealed-secrets-controller --controller-namespace=sealed-secrets > sealing-key.crt

# Or if you already have it locally:
cat sealing-key.crt
```

Use `kubeseal` CLI to encrypt secrets:

```bash
# Example: Seal a secret
kubectl create secret generic my-secret \
  --from-literal=password=supersecret \
  --dry-run=client -o yaml | \
kubeseal --cert sealing-key.crt -o yaml > my-sealed-secret.yaml

# Commit my-sealed-secret.yaml to Git safely!
git add my-sealed-secret.yaml
git commit -m "Add sealed secret for my-app"
git push
```

### Immediate Post-Bootstrap Tasks

1. **Verify ArgoCD Application Health**
   ```bash
   kubectl get applications -n argocd
   # All should eventually show Synced + Healthy
   ```

2. **Check Infrastructure Components**
   ```bash
   # Traefik
   kubectl get pods -n traefik

   # cert-manager
   kubectl get pods -n cert-manager

   # sealed-secrets
   kubectl get pods -n sealed-secrets

   # Storage (if applicable)
   kubectl get pods -n storage
   ```

3. **Monitor Certificate Issuance**
   ```bash
   kubectl get certificate -A
   kubectl get clusterissuer

   # Check cert-manager logs if certificates are stuck
   kubectl logs -n cert-manager -l app=cert-manager
   ```

4. **Verify Hetzner DNS Webhook**
   ```bash
   kubectl get pods -n cert-manager -l app.kubernetes.io/name=cert-manager-webhook-hetzner
   kubectl logs -n cert-manager -l app.kubernetes.io/name=cert-manager-webhook-hetzner
   ```

5. **Configure Traefik IngressRoute for ArgoCD**

   Once Traefik is healthy and certificates are issued, ArgoCD should be accessible at:
   ```
   https://argocd.orchard.homehill.de
   ```

   Stop the port-forward (Ctrl+C) and access ArgoCD via the IngressRoute instead.

6. **Change ArgoCD Admin Password**
   ```bash
   argocd account update-password
   ```

### Ongoing Cluster Management

- **GitOps Workflow:** All changes should go through Git commits to the `new_season` branch
- **ArgoCD Auto-Sync:** Applications with `syncPolicy.automated` will auto-deploy on Git changes
- **Manual Sync:** Use ArgoCD UI or CLI to manually sync applications when needed
- **Monitoring:** Set up monitoring stack (VictoriaMetrics, Grafana) once base infra is stable

---

## 📝 Notes & Best Practices

### k3s Built-in Components

- **Traefik:** Disabled at install time (`--disable traefik`) because we manage our own via ArgoCD
- **Flannel CNI:** Enabled by default with VXLAN backend - no separate installation needed
- **CoreDNS:** Included and enabled by default
- **ServiceLB:** Included (LoadBalancer implementation for k3s)
- **Local Path Provisioner:** Included (default StorageClass for local volumes)

### DNS Resolution

All nodes use **FQDN** (Fully Qualified Domain Names):
- 🍎 `apple.homehill.de` → `192.168.1.50` (control plane)
- 🍋 `lemon.homehill.de` → `192.168.1.51` (worker)
- 🍑 `plum.homehill.de` → `192.168.1.52` (worker)

Ensure these hostnames resolve correctly via:
- Pi-hole or local DNS server
- `/etc/hosts` on all nodes (fallback)

### Public Repository

The `homehill` repository is **public**, so:
- ✅ No SSH keys needed
- ✅ No Git credentials secrets
- ✅ ArgoCD clones via HTTPS anonymously
- ⚠️ Never commit sensitive data (use SealedSecrets!)

### Idempotency

This bootstrap process is **mostly idempotent**:
- ✅ Re-running ArgoCD Application apply is safe
- ✅ Re-running Helm installs with `--wait` is safe (will upgrade if already installed)
- ⚠️ Re-running k3s control plane install will **reset the cluster** - don't do this!
- ⚠️ Re-running k3s agent install will **re-join** the node - usually safe but may cause brief disruption

### Node Token Security

The k3s node token is a **cluster-wide shared secret**:
- 🔒 Keep it secret! Anyone with the token can join nodes to your cluster
- 🔄 Token is generated once during control plane init
- 📍 Stored in `/var/lib/rancher/k3s/server/node-token` on control plane
- 🔐 Can be rotated by regenerating the control plane (requires cluster rebuild)

### Certificate Rotation

k3s automatically manages certificate rotation:
- Kubernetes API server certificates are rotated 90 days before expiry
- Kubelet certificates are rotated automatically
- No manual intervention needed

---

## 🐛 Troubleshooting

### Worker Nodes Won't Join

**Symptom:** Worker nodes stuck in "NotReady" or not appearing in `kubectl get nodes`

**Possible causes:**
1. **Wrong K3S_URL:** Check that `apple.homehill.de:6443` is reachable from worker node
   ```bash
   # From worker node:
   curl -k https://apple.homehill.de:6443
   # Should return some JSON (forbidden error is OK - means API is reachable)
   ```

2. **Wrong K3S_TOKEN:** Re-check the node token from `/var/lib/rancher/k3s/server/node-token`

3. **Firewall blocking:** Ensure port 6443 is open on control plane node

4. **DNS resolution failed:** Check if `apple.homehill.de` resolves correctly
   ```bash
   # From worker node:
   nslookup apple.homehill.de
   # Should return 192.168.1.50
   ```

### ArgoCD Applications Stuck "Progressing"

**Symptom:** Applications show "Progressing" for more than 5 minutes

**Possible causes:**
1. **Image pull errors:** Check pod events: `kubectl describe pod <pod-name> -n <namespace>`
2. **Missing dependencies:** Check if dependent apps (cert-manager, sealed-secrets) are healthy first
3. **Insufficient resources:** Check node resources: `kubectl top nodes`

### Certificates Not Issuing

**Symptom:** Certificate stuck in "Pending" state

**Check:**
```bash
# Check certificate status
kubectl describe certificate homehill-wildcard -n default

# Check challenges
kubectl get challenges -A

# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager -f

# Check webhook logs
kubectl logs -n cert-manager -l app.kubernetes.io/name=cert-manager-webhook-hetzner -f
```

**Common issues:**
- Hetzner API token invalid or expired
- DNS propagation delay (wait 2-3 minutes)
- Webhook not running or crashed

### SealedSecrets Cannot Decrypt

**Symptom:** Pods fail to start with "SealedSecret cannot be decrypted" errors

**Possible causes:**
1. **Wrong private key installed:** You installed a different key than was used to encrypt the secrets
   ```bash
   # Check which key is active
   kubectl get secret -n sealed-secrets sealed-secrets-key -o yaml
   
   # Compare fingerprint with your backup
   openssl x509 -in sealing-key.crt -noout -fingerprint
   ```

2. **Sealed-secrets controller not using the key:** Ensure you labeled the secret and restarted the controller (see "Install Sealed Secrets Private Key" section)

3. **Namespace mismatch:** SealedSecrets are namespace-scoped by default. Ensure the SealedSecret is in the correct namespace.

---

## 🦊 Credits

**Documentation by:** Ana 🦊 (Coding with Ana Space)  
**Cluster Design:** Headphonebear 🐻 & Ana 🦊  
**Updated:** February 15, 2026  
**Location:** Kiel, Germany 🇩🇪  

---

**Built with ❤️, Club Mate 🍵, and binary algebra ✨**

*"Never Stop Running" - homehill philosophy*

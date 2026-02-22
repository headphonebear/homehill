# 🔐 Secrets Management with SealedSecrets

**How to safely store secrets in Git**

This guide explains how we manage sensitive data (passwords, API tokens, TLS keys) in the Homehill cluster using **Sealed Secrets**.

---

## 🤔 Why SealedSecrets?

**The Problem:**

Kubernetes Secrets are base64-encoded, **not encrypted**. Storing them in Git exposes sensitive data:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
data:
  password: cGFzc3dvcmQxMjM=  # ❌ Anyone can decode this!
```

```bash
echo "cGFzc3dvcmQxMjM=" | base64 -d
# Output: password123
```

**The Solution:**

**SealedSecrets** encrypt secrets using the cluster's public key. Only the cluster can decrypt them.

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: my-secret
spec:
  encryptedData:
    password: AgB7t9... # ✅ Encrypted! Safe to commit to Git
```

**Workflow:**

1. Create a normal Kubernetes Secret (locally, never commit!)
2. Encrypt it with `kubeseal` → SealedSecret
3. Commit the SealedSecret to Git
4. SealedSecrets controller decrypts it in the cluster → normal Secret
5. Apps consume the decrypted Secret

---

## 🛠️ Prerequisites

### Install kubeseal CLI

**macOS (Homebrew):**
```bash
brew install kubeseal
```

**Linux:**
```bash
VERSION=$(curl -s https://api.github.com/repos/bitnami-labs/sealed-secrets/releases/latest | grep tag_name | cut -d '"' -f 4 | cut -c 2-)
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v${VERSION}/kubeseal-${VERSION}-linux-amd64.tar.gz
tar -xzf kubeseal-${VERSION}-linux-amd64.tar.gz
sudo mv kubeseal /usr/local/bin/
```

**Verify:**
```bash
kubeseal --version
```

### Check SealedSecrets Controller is Running

```bash
kubectl -n kube-system get pods | grep sealed-secrets
```

Expected output:
```
sealed-secrets-controller-xxxxx   1/1     Running   0   5d
```

---

## 🆕 Creating a New SealedSecret

### Example: API Token

Let's create a SealedSecret for the Hetzner DNS API token.

**Step 1: Create a normal Secret (dry-run, don't apply)**

```bash
kubectl create secret generic hetzner-token \
  --namespace=cert-manager \
  --from-literal=api-token=YOUR_ACTUAL_TOKEN_HERE \
  --dry-run=client -o yaml > hetzner-token-plain.yaml
```

**Output:** `hetzner-token-plain.yaml` (don't commit this!)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: hetzner-token
  namespace: cert-manager
data:
  api-token: WU9VUl9BQ1RVQUxfVE9LRU5fSEVSRQ==  # ❌ Base64, not secure!
```

**Step 2: Seal the Secret**

```bash
kubeseal -o yaml < hetzner-token-plain.yaml > hetzner-token-sealed.yaml
```

**Output:** `hetzner-token-sealed.yaml` (safe to commit!)
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: hetzner-token
  namespace: cert-manager
spec:
  encryptedData:
    api-token: AgB7t9k3... # ✅ Encrypted with cluster public key
  template:
    metadata:
      name: hetzner-token
      namespace: cert-manager
```

**Step 3: Commit and Push**

```bash
rm hetzner-token-plain.yaml  # Delete plaintext!
git add hetzner-token-sealed.yaml
git commit -m "add: Hetzner API token for cert-manager"
git push
```

**Step 4: Apply (if not using GitOps)**

```bash
kubectl apply -f hetzner-token-sealed.yaml
```

The SealedSecrets controller will decrypt it and create a normal Secret:

```bash
kubectl -n cert-manager get secret hetzner-token
```

---

## 🔄 Updating an Existing SealedSecret

**Scenario:** The Hetzner API token rotated. You need to update the secret.

**Step 1: Create Updated Secret (dry-run)**

```bash
kubectl create secret generic hetzner-token \
  --namespace=cert-manager \
  --from-literal=api-token=NEW_TOKEN_HERE \
  --dry-run=client -o yaml > hetzner-token-updated.yaml
```

**Step 2: Seal It**

```bash
kubeseal -o yaml < hetzner-token-updated.yaml > hetzner-token-sealed.yaml
```

This **overwrites** the old sealed secret file.

**Step 3: Commit and Push**

```bash
rm hetzner-token-updated.yaml
git add hetzner-token-sealed.yaml
git commit -m "update: Rotate Hetzner API token"
git push
```

**Step 4: Verify**

```bash
# The controller auto-updates the Secret
kubectl -n cert-manager get secret hetzner-token -o yaml

# Restart pods using the secret (if needed)
kubectl -n cert-manager rollout restart deployment cert-manager-webhook-hetzner
```

---

## 📝 Creating Secrets from Files

### Example: TLS Certificate

```bash
# Create secret from cert files
kubectl create secret tls my-tls-secret \
  --namespace=default \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  --dry-run=client -o yaml | kubeseal -o yaml > my-tls-sealed.yaml

# Commit
git add my-tls-sealed.yaml
git commit -m "add: TLS cert for my-service"
git push
```

### Example: SSH Key

```bash
kubectl create secret generic github-ssh-key \
  --namespace=argocd \
  --from-file=id_rsa=/path/to/private_key \
  --from-file=id_rsa.pub=/path/to/public_key \
  --dry-run=client -o yaml | kubeseal -o yaml > github-ssh-sealed.yaml
```

---

## 🕵️ Viewing Encrypted Secrets

**SealedSecret (encrypted, in Git):**
```bash
cat hetzner-token-sealed.yaml
```

You'll see `encryptedData` - this is **safe** to view.

**Decrypted Secret (in cluster):**
```bash
# View the decrypted secret (requires cluster access)
kubectl -n cert-manager get secret hetzner-token -o yaml

# Decode a specific key
kubectl -n cert-manager get secret hetzner-token -o jsonpath="{.data.api-token}" | base64 -d
```

⚠️ **Security:** Only cluster admins with `kubectl` access can view decrypted secrets!

---

## 🚨 Troubleshooting

### Error: "no key could decrypt secret"

**Symptoms:**
```bash
kubectl apply -f my-sealed-secret.yaml
Error: no key could decrypt secret
```

**Cause:** The SealedSecret was encrypted with a **different cluster's public key**.

**Fix:**

1. **Get the current cluster's public cert:**
   ```bash
   kubeseal --fetch-cert > pub-cert.pem
   ```

2. **Re-seal the secret:**
   ```bash
   kubeseal --cert=pub-cert.pem -o yaml < my-secret-plain.yaml > my-sealed-secret.yaml
   ```

3. **Apply and commit:**
   ```bash
   kubectl apply -f my-sealed-secret.yaml
   git add my-sealed-secret.yaml
   git commit -m "fix: Re-seal secret for current cluster"
   git push
   ```

### SealedSecret Applied but Secret Not Created

**Diagnosis:**
```bash
# Check SealedSecret exists
kubectl -n <namespace> get sealedsecret

# Check controller logs
kubectl -n kube-system logs -l name=sealed-secrets-controller
```

**Common Issues:**
- Controller not running (check pod status)
- RBAC permissions missing (controller can't create Secrets)
- Invalid YAML format in SealedSecret

**Fix:**
```bash
# Restart controller
kubectl -n kube-system rollout restart deployment sealed-secrets-controller

# Reapply SealedSecret
kubectl apply -f my-sealed-secret.yaml
```

### Accidentally Committed Plaintext Secret to Git

🚨 **EMERGENCY:** Your plaintext secret is now in Git history!

**Immediate Actions:**

1. **Rotate the secret** (change password, regenerate API token, etc.)
2. **Remove from Git history:**
   ```bash
   # Remove file from history (use BFG Repo-Cleaner)
   brew install bfg
   bfg --delete-files hetzner-token-plain.yaml
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push --force
   ```

3. **Create a new SealedSecret** with the rotated credentials

**Prevention:** Add to `.gitignore`:
```
*-plain.yaml
*-plaintext.yaml
*-unencrypted.yaml
```

---

## 🔑 Emergency: Recover Lost Sealing Key

**Scenario:** Cluster reinstalled, old SealedSecrets can't be decrypted.

**The sealing key is stored in the cluster:**

```bash
# Backup sealing key BEFORE disaster
kubectl -n kube-system get secret sealed-secrets-key -o yaml > sealed-secrets-key-backup.yaml
```

**Store this backup SECURELY** (not in Git! Use 1Password, Bitwarden, etc.)

**To restore:**

```bash
# After cluster rebuild, restore the key
kubectl apply -f sealed-secrets-key-backup.yaml

# Restart controller
kubectl -n kube-system rollout restart deployment sealed-secrets-controller
```

Now old SealedSecrets will decrypt correctly.

---

## 🛡️ Security Best Practices

### ✅ DO

- **Encrypt all secrets** before committing to Git
- **Delete plaintext files** immediately after sealing
- **Backup the sealing key** to secure storage (outside Git)
- **Rotate secrets** regularly (especially after team changes)
- **Use namespace scoping** (secrets can only be used in specific namespaces)
- **Audit Git history** for accidental plaintext commits

### ❌ DON'T

- **Don't commit plaintext secrets** to Git
- **Don't share sealed secrets** across clusters (they won't decrypt)
- **Don't store sealing key backup** in the same repo
- **Don't use `--scope cluster-wide`** unless necessary (reduces security)
- **Don't forget to rotate** secrets after team members leave

---

## 📚 Reference

### Useful Commands Cheat Sheet

```bash
# Create sealed secret from literal
kubectl create secret generic <name> --from-literal=key=value --dry-run=client -o yaml | kubeseal -o yaml > <name>-sealed.yaml

# Create sealed secret from file
kubectl create secret generic <name> --from-file=<path> --dry-run=client -o yaml | kubeseal -o yaml > <name>-sealed.yaml

# Fetch cluster public cert
kubeseal --fetch-cert > pub-cert.pem

# Seal with specific cert
kubeseal --cert=pub-cert.pem -o yaml < plain.yaml > sealed.yaml

# View decrypted secret
kubectl get secret <name> -o yaml

# Decode secret value
kubectl get secret <name> -o jsonpath="{.data.<key>}" | base64 -d

# Backup sealing key
kubectl -n kube-system get secret sealed-secrets-key -o yaml > backup.yaml
```

### SealedSecret Scopes

| Scope | Description | Use Case |
|-------|-------------|----------|
| `strict` (default) | Sealed to namespace + name | Most secure, prevents reuse |
| `namespace-wide` | Sealed to namespace only | Secret can be renamed |
| `cluster-wide` | Works in any namespace | Less secure, use sparingly |

**Example:**
```bash
kubeseal --scope namespace-wide -o yaml < plain.yaml > sealed.yaml
```

---

## 🔗 External Resources

- **Official Docs:** https://sealed-secrets.netlify.app/
- **GitHub Repo:** https://github.com/bitnami-labs/sealed-secrets
- **Kubeseal Releases:** https://github.com/bitnami-labs/sealed-secrets/releases

---

**Keep your secrets sealed!** 🔐💪

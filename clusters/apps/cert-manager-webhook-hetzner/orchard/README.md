# Cert-Manager Hetzner Webhook Setup

## What is this?

This directory contains the complete setup for automatic TLS certificate management using:

- **cert-manager**: Kubernetes certificate controller
- **Hetzner DNS Webhook**: DNS01 challenge solver for Let's Encrypt
- **Let's Encrypt**: Free, automated TLS certificates

## Architecture

Certificate Request
↓
ClusterIssuer (letsencrypt-prod)
↓
DNS01 Challenge via Hetzner Webhook
↓
Webhook reads Hetzner API Token from Secret
↓
Webhook creates TXT record: _acme-challenge.homehill.de
↓
Let's Encrypt validates TXT record
↓
Certificate issued and stored in Secret
↓
Traefik uses Secret for TLS termination


## Files

- **Chart.yaml**: Helm chart definition with Hetzner webhook dependency
- **values.yaml**: Webhook configuration (groupName: acme.homehill.de)
- **templates/hetzner-rbac.yaml**: RBAC permissions for webhook to read secrets
- **templates/hetzner-token-sealed.yaml**: Encrypted Hetzner DNS API token
- **templates/clusterissuer.yaml**: Let's Encrypt ClusterIssuer configuration
- **templates/wildcard-certificate.yaml**: Wildcard cert for *.homehill.de

## How it works

1. **Webhook Deployment**: ArgoCD deploys the Hetzner webhook from Helm chart
2. **RBAC Setup**: Webhook gets permission to read secrets in cert-manager namespace
3. **Secret Unsealing**: Sealed-secrets controller decrypts the Hetzner API token
4. **ClusterIssuer Creation**: Cert-manager registers the Let's Encrypt issuer
5. **Certificate Request**: Wildcard certificate triggers DNS01 challenge
6. **DNS Challenge**: Webhook uses Hetzner API to create TXT record
7. **Validation**: Let's Encrypt checks TXT record and issues certificate
8. **Secret Storage**: Certificate stored in `homehill-wildcard-tls` secret
9. **Auto-Renewal**: Cert-manager renews 30 days before expiry

## Important Notes

### groupName Consistency

The `groupName` must be **identical** in:
- `values.yaml`: `webhook.groupName: acme.homehill.de`
- `clusterissuer.yaml`: `spec.acme.solvers[0].dns01.webhook.groupName: acme.homehill.de`

### Secret Name/Key Consistency

The secret reference must match:
- **Secret name**: `hetzner` (not `hetzner-dns-token`!)
- **Secret key**: `token` (not `api-key`!)
- **ClusterIssuer ref**: `tokenSecretKeyRef.name: hetzner`, `key: token`

### SealedSecret Re-encryption

If the new cluster uses a different sealing key, re-seal the secret:

```bash
# Get current Hetzner token (if you have it as plain text)
echo -n "your-hetzner-token-here" | kubectl create secret generic hetzner \
  --namespace=cert-manager \
  --from-file=token=/dev/stdin \
  --dry-run=client -o yaml | \
  kubeseal --cert sealing-key.crt -o yaml > templates/hetzner-token-sealed.yaml
Deployment

This app is managed by ArgoCD. To deploy:

bash
# Apply ArgoCD Application (from clusters/argocd/)
kubectl apply -f clusters/argocd/cert-manager-webhook-hetzner.yaml

ArgoCD will automatically sync and deploy all resources.
Debugging
Check webhook logs

bash
kubectl logs -n cert-manager -l app.kubernetes.io/name=cert-manager-webhook-hetzner

Check cert-manager logs

bash
kubectl logs -n cert-manager -l app=cert-manager

Check certificate status

bash
kubectl get certificate -A
kubectl describe certificate homehill-wildcard -n default

Check challenge status

bash
kubectl get challenge -A
kubectl describe challenge <challenge-name> -n default

Manual DNS test

bash
# Check if TXT record was created
dig TXT _acme-challenge.homehill.de @ns1.first-ns.de

Migration from first-season
Changes from old setup:

    ✅ Fixed groupName: Changed from acme.hetzner.com to acme.homehill.de

    ✅ Fixed secret name: Changed from hetzner-dns-token to hetzner

    ✅ Fixed secret key: Changed from api-key to token

    ✅ Added RBAC: Explicit secret read permissions for webhook

    ✅ Helm structure: Using Chart.yaml with dependency instead of separate ArgoCD app

Built with 🦊 by Ana & 🐻 by Headphonebear
Friday, February 13, 2026 - Kiel, Germany
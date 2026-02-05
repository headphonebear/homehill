# cert-manager with Hetzner DNS Webhook

## Setup (2026-02-01)

### Installation
- cert-manager installed via Helm
- Hetzner DNS API token stored as secret `hetzner` in namespace `cert-manager`
- cert-manager-webhook-hetzner installed

### ClusterIssuer
- `letsencrypt-prod` using DNS-01 challenge via Hetzner webhook
- Wildcard certificate for `*.homehill.de` and `homehill.de`

### Certificate Renewal
- Automatic renewal every 60 days (certificate valid for 90 days)
- Webhook uses Hetzner DNS API automatically

### Secret
- Name: `homehill-wildcard-tls`
- Namespace: `default`
- Usage in Ingress: `spec.tls.secretName`

### Files
- ClusterIssuer & Certificate: `clusters/orchard/apps/cert-manager/clusterissuer-and-cert.yaml`

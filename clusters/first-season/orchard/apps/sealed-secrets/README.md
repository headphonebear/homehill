## Implementation Complete ✅

### What was done:
- Installed sealed-secrets v0.27.0 via ArgoCD (kube-system namespace)
- Generated cluster-specific sealing key
- Created SealedSecret for hetzner-dns-token (cert-manager namespace)
- Token encrypted and stored in Git: `clusters/orchard/apps/sealed-secrets/hetzner-token-sealed.yaml`

### How it works:
- SealedSecret can only be decrypted by THIS cluster's sealing key
- Safe to commit to Git (token is encrypted, not plaintext)
- ArgoCD reads the sealed secret and auto-unseals it
- Next: Use in cert-manager ClusterIssuer (C1)

### CLI used:
- kubeseal v0.27.0 (bitnami-labs helm repo)
- Sealed with: `--controller-name=sealed-secrets --controller-namespace=kube-system`

### Testing:
```bash
kubectl get sealedsecret -n cert-manager
kubectl describe sealedsecret hetzner-dns-token -n cert-manager
```

### Next steps:

- C1: Create Hetzner webhook + ClusterIssuer to use this token
- Later: Consider sealed-secrets rotation policy

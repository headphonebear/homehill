# Longhorn Storage

GitOps-managed via ArgoCD.

## Configuration
- Chart: longhorn 1.10.1
- Replicas: 3 (across apple, lemon, plum)
- Data Path: /mnt/longhorn (900GB per node)
- Default StorageClass: Yes

## Status
- Pre-Sync: Upgrade hooks ✅
- Sync: All resources healthy ✅
- Post-Sync: Upgrade finalization ✅

## Next: Backup Policy (separate ticket!)

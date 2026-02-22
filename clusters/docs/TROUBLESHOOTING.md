# 🚨 Troubleshooting Guide

**Battle-tested fixes for Homehill cluster issues**

This guide documents real problems encountered in production and their solutions. Every fix here has been tested in the field.

---

## 🛠️ Quick Diagnostic Commands

```bash
# Overall cluster health
kubectl get nodes
kubectl get pods -A | grep -v Running | grep -v Completed

# ArgoCD app status
argocd app list
argocd app get <app-name>

# Recent events (last 20)
kubectl get events -A --sort-by='.lastTimestamp' | tail -20

# Pod logs (when pod is failing)
kubectl -n <namespace> logs <pod-name>
kubectl -n <namespace> logs <pod-name> -c <container-name>  # For multi-container pods

# Describe resources (shows events + config)
kubectl -n <namespace> describe pod <pod-name>
kubectl -n <namespace> describe pvc <pvc-name>
```

---

## 💥 Multi-Attach Errors

### Symptoms

```
Multi-Attach error for volume "pvc-xxx" 
Volume is already used by pod(s) <old-pod-name>
```

Pod stuck in `Init:0/1` or `Pending` state.

### Root Cause

Kubernetes PVCs with `accessMode: ReadWriteOnce` can only be mounted by **one pod at a time**. This happens when:

1. **Deployment rollout creates new pod** (e.g., config change)
2. **Old pod still exists** (graceful termination takes 30-60s)
3. **New pod tries to mount the same PVC** → ❌ blocked!

Common triggers:
- ArgoCD `selfHeal: true` causing frequent re-deploys
- Grafana Secret drift (random password regeneration)
- Manual `kubectl apply` overlapping with existing pod

### Fix: Force Delete the Old Pod

```bash
# Find the blocking pod (shown in error message)
kubectl -n <namespace> get pods | grep <app-name>

# Force delete the old pod
kubectl -n <namespace> delete pod <old-pod-name> --force --grace-period=0

# Watch new pod start
kubectl -n <namespace> get pods -w
```

**Example:**
```bash
kubectl -n monitoring delete pod monitoring-grafana-f76bcc4c6-clgwd --force --grace-period=0
```

### Prevention: Disable selfHeal for Apps with RWO PVCs

In `clusters/argocd/orchard/<app>.yaml`:

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: false  # ← CRITICAL for apps with ReadWriteOnce PVCs
```

**Why?** Prevents ArgoCD from auto-syncing on every config drift, reducing rollout frequency.

### Prevention: Set replicas: 1 Explicitly

Some Helm charts default to `replicas: 2` for HA. Override in values.yaml:

```yaml
grafana:
  replicas: 1  # ← Cannot scale with ReadWriteOnce PVC
```

---

## 🔐 Webhook TLS Errors

### Symptoms

Prometheus Operator logs filled with:

```
Failed to call webhook: Post "https://...": tls: failed to verify certificate
TLS handshake error from ...: remote error: tls: bad certificate
```

Prometheus StatefulSet not created or stuck.

### Root Cause

Admission webhooks validate Prometheus/Alertmanager CRs before creation. They require:
1. Valid TLS certificates (usually from cert-manager)
2. Webhook service running and reachable
3. Correct CA bundle in webhook config

**In homelab:** Cert-manager might not be ready yet (bootstrap race condition), or webhook certs expired.

### Fix: Disable Admission Webhooks

For homelab use, webhook validation is **nice-to-have but not critical**.

In `clusters/apps/monitoring/orchard/values.yaml`:

```yaml
prometheusOperator:
  admissionWebhooks:
    enabled: false  # ← Disables webhook validation
```

**Trade-off:** Invalid Prometheus CRs won't be caught at admission time (will fail at reconcile instead).

**Benefit:** Clean logs, faster bootstrap, no cert-manager dependency.

### Alternative: Fix Webhook Certificates

If you want to keep webhooks enabled:

```bash
# Check webhook pods
kubectl -n monitoring get pods | grep operator

# Check webhook service
kubectl -n monitoring get svc | grep webhook

# Check webhook TLS secret
kubectl -n monitoring get secret | grep webhook

# Restart operator to regenerate certs
kubectl -n monitoring rollout restart deployment monitoring-kube-prometheus-operator
```

---

## 🔄 ArgoCD Stuck in "Progressing"

### Symptoms

ArgoCD UI shows app status: **Progressing** for >10 minutes.

No errors in ArgoCD logs, but app never becomes "Healthy".

### Root Cause

ArgoCD waits for all resources to reach "healthy" state. Common blockers:

1. **Pods not starting** (ImagePullBackOff, CrashLoopBackOff)
2. **PVCs not bound** (StorageClass missing, Longhorn not ready)
3. **Helm hooks stuck** (pre-install/post-install jobs failing)
4. **Resource quotas exceeded** (CPU/memory limits)

### Diagnosis

```bash
# Check what's not healthy
argocd app get <app-name>

# Look for non-Running pods
kubectl -n <namespace> get pods

# Check pod details
kubectl -n <namespace> describe pod <pod-name>

# Check PVC status
kubectl -n <namespace> get pvc
```

### Common Fixes

**ImagePullBackOff:**
```bash
# Check image name in deployment
kubectl -n <namespace> get deployment <name> -o yaml | grep image:

# Check ImagePullSecrets if using private registry
kubectl -n <namespace> get secrets
```

**PVC Not Bound:**
```bash
# Check StorageClass exists
kubectl get storageclass

# Check Longhorn is running
kubectl -n longhorn-system get pods

# Describe PVC for events
kubectl -n <namespace> describe pvc <pvc-name>
```

**CrashLoopBackOff:**
```bash
# Get pod logs
kubectl -n <namespace> logs <pod-name>

# Previous container logs (if pod restarted)
kubectl -n <namespace> logs <pod-name> --previous
```

---

## 📜 Certificate Not Issued

### Symptoms

```bash
kubectl get certificate
NAME                 READY   SECRET               AGE
homehill-wildcard    False   homehill-wildcard-tls   10m
```

Traefik shows **TLS handshake errors** or **self-signed certificate**.

### Diagnosis

```bash
# Check Certificate status
kubectl describe certificate homehill-wildcard

# Check CertificateRequest
kubectl get certificaterequest
kubectl describe certificaterequest <name>

# Check Order (ACME challenge)
kubectl get order
kubectl describe order <name>

# Check Challenge
kubectl get challenge
kubectl describe challenge <name>

# Check cert-manager logs
kubectl -n cert-manager logs -l app=cert-manager

# Check webhook logs (if using Hetzner webhook)
kubectl -n cert-manager logs -l app.kubernetes.io/name=cert-manager-webhook-hetzner
```

### Common Issues

**DNS01 Challenge Failing:**

```bash
# Check Hetzner API token secret
kubectl -n cert-manager get secret hetzner -o yaml

# Test DNS propagation (from outside cluster)
dig TXT _acme-challenge.homehill.de

# Check webhook can reach Hetzner API
kubectl -n cert-manager logs -l app.kubernetes.io/name=cert-manager-webhook-hetzner | grep -i error
```

**ClusterIssuer Not Ready:**

```bash
# Check ClusterIssuer status
kubectl get clusterissuer
kubectl describe clusterissuer letsencrypt-prod

# Check Let's Encrypt account registration
kubectl get secret letsencrypt-key-prod -o yaml
```

**Rate Limit Hit:**

Let's Encrypt production has rate limits:
- **50 certificates per domain per week**
- **5 failed validations per hour**

If hit, use **Staging** instead:

```yaml
# In clusterissuer.yaml
server: https://acme-staging-v02.api.letsencrypt.org/directory
```

Staging certs are **not trusted by browsers** but don't count against rate limits.

---

## 💾 Longhorn Volume Issues

### Volume Stuck in "Attaching"

**Symptoms:**
```bash
kubectl -n longhorn-system get volumes
NAME         STATE       ROBUSTNESS   SCHEDULED   SIZE   NODE   AGE
pvc-xxx      attaching   unknown      True        10Gi   plum   5m
```

**Fix:**
```bash
# Check Longhorn manager logs
kubectl -n longhorn-system logs -l app=longhorn-manager

# Check node where volume should attach
kubectl describe node <node-name>

# Force detach (if pod already deleted)
kubectl -n longhorn-system patch volume <volume-name> -p '{"spec":{"nodeID":""}}' --type=merge
```

### Volume Degraded (Replica Lost)

**Symptoms:**
```bash
kubectl -n longhorn-system get volumes
NAME         STATE     ROBUSTNESS   SCHEDULED   SIZE   
pvc-xxx      attached  degraded     True        10Gi
```

**Cause:** One of the replicas failed (node down, disk full).

**Fix:**

1. **Check replica status:**
   ```bash
   kubectl -n longhorn-system get replicas | grep <volume-name>
   ```

2. **Check node health:**
   ```bash
   kubectl get nodes
   kubectl -n longhorn-system get nodes  # Longhorn nodes
   ```

3. **If node is down:** Longhorn will auto-rebuild replica on another node

4. **If disk full:** Free space or add more storage

5. **Manual rebuild:**
   - Go to Longhorn UI: `kubectl port-forward -n longhorn-system svc/longhorn-frontend 8080:80`
   - Select volume → "Salvage" or "Rebuild"

---

## 🔁 ArgoCD Sync Loops

### Symptoms

ArgoCD constantly syncs an app (every few minutes) even when Git hasn't changed.

App status flips between "Synced" and "OutOfSync".

### Root Cause

Some resources have **mutable fields** that change at runtime:

- Grafana admin password Secret (regenerated on every sync)
- Pod status fields (`lastTransitionTime`, etc.)
- LoadBalancer IPs assigned by cloud provider

**If `selfHeal: true`:** ArgoCD sees drift → syncs → creates new pod → old pod terminates → Multi-Attach error!

### Fix: Disable selfHeal

In `clusters/argocd/orchard/<app>.yaml`:

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: false  # ← Prevents sync loops
```

**Manual sync when needed:**
```bash
argocd app sync <app-name>
```

### Fix: Ignore Mutable Fields

Tell ArgoCD to ignore specific fields:

```yaml
syncPolicy:
  syncOptions:
    - RespectIgnoreDifferences=true
  ignoreDifferences:
    - group: ""
      kind: Secret
      name: monitoring-grafana
      jsonPointers:
        - /data/admin-password  # Ignore password changes
```

---

## 🧹 Cleanup Commands

### Remove Stuck Finalizers

If a resource won't delete:

```bash
# Edit and remove finalizers
kubectl edit <resource-type> <name>

# Remove "finalizers:" section, save and exit
```

### Force Delete Namespace

```bash
kubectl get namespace <namespace> -o json | \
  jq '.spec.finalizers = []' | \
  kubectl replace --raw "/api/v1/namespaces/<namespace>/finalize" -f -
```

### Clean Up Old ReplicaSets

```bash
# Delete ReplicaSets with 0 pods
kubectl -n <namespace> get rs | grep ' 0 ' | awk '{print $1}' | xargs kubectl -n <namespace> delete rs
```

### Restart All Pods in Deployment

```bash
kubectl -n <namespace> rollout restart deployment <name>
```

---

## 📞 Need More Help?

**Check logs first:**
```bash
kubectl -n <namespace> logs <pod-name>
```

**Describe the resource:**
```bash
kubectl -n <namespace> describe <resource-type> <name>
```

**Check recent events:**
```bash
kubectl get events -A --sort-by='.lastTimestamp' | tail -50
```

**Still stuck?** Open an issue in the repo with:
1. What you tried to do
2. What happened instead
3. Relevant logs and `describe` output

---

**May your pods always be Running!** 🚀💪

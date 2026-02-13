# 🍎 Orchard Cluster - Post-Bootstrap Tasks

This document contains **all TODO items** from the cluster configuration, organized by **priority and phase**.

After successfully bootstrapping the Orchard cluster, work through these tasks **in order** to bring the cluster to full operational status.

---

## ✅ Bootstrap Checklist

Before starting these tasks, ensure bootstrap is complete:

- [ ] k3s control plane running on apple.homehill.de (192.168.1.50) 🍎
- [ ] Worker nodes joined: lemon.homehill.de (192.168.1.51) 🍋, plum.homehill.de (192.168.1.52) 🍑
- [ ] ArgoCD deployed and accessible via port-forward
- [ ] All ArgoCD Applications synced and healthy (`kubectl get applications -n argocd`)

---

## 🚀 PHASE 1: Critical First Steps

**Priority: CRITICAL - Do these immediately after bootstrap!**

### 1.1 Security - Change Grafana Admin Password ⚠️

**WHY:** Default password is a security risk!

**Steps:**
```bash
# Get the auto-generated password
kubectl -n monitoring get secret monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d
echo

# Access Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80

# Open browser: http://localhost:3000
# Login: admin / <password from above>
# Go to: Settings → Users → admin → Change Password
```

**Alternative (GitOps):**
- Create SealedSecret with new password
- Update monitoring values.yaml to reference it

---

### 1.2 Storage - Test Disaster Recovery 🧪

**WHY:** Verify 3-way replication works BEFORE production data!

**Steps:**
```bash
# 1. Create a test volume
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-volume
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn
  resources:
    requests:
      storage: 1Gi
EOF

# 2. Create test pod that writes data
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: test-writer
  namespace: default
spec:
  containers:
  - name: writer
    image: alpine:latest
    command: ["/bin/sh", "-c"]
    args:
      - |
        echo "Test data at $(date)" > /data/test.txt
        while true; do
          echo "$(date): Still alive" >> /data/test.txt
          sleep 60
        done
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: test-volume
EOF

# 3. Wait for pod to write data
kubectl wait --for=condition=Ready pod/test-writer -n default --timeout=60s
sleep 10

# 4. Verify data exists
kubectl exec -n default test-writer -- cat /data/test.txt

# 5. Simulate node failure (drain lemon)
kubectl drain lemon.homehill.de --ignore-daemonsets --delete-emptydir-data

# 6. Verify pod reschedules and data persists
kubectl get pods -n default -o wide
# Pod should restart on apple or plum
kubectl wait --for=condition=Ready pod/test-writer -n default --timeout=120s
kubectl exec -n default test-writer -- cat /data/test.txt
# Should show same data!

# 7. Restore node
kubectl uncordon lemon.homehill.de

# 8. Cleanup
kubectl delete pod test-writer -n default
kubectl delete pvc test-volume -n default
```

**Expected result:** Data survives node failure! ✅

---

### 1.3 Monitoring - Access Dashboards 📊

**Steps:**
```bash
# Access Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# Open: http://localhost:3000

# Access VictoriaMetrics UI (optional)
kubectl port-forward -n monitoring svc/victoriametrics-victoria-metrics-single-server 8428:8428
# Open: http://localhost:8428/vmui
```

**Verify:**
- [ ] Grafana loads
- [ ] Both data sources exist: Prometheus (default) + VictoriaMetrics
- [ ] Default dashboards show data

---

## 📈 PHASE 2: Essential Dashboards & Monitoring

**Priority: HIGH - Essential for cluster visibility**

### 2.1 Import Grafana Dashboards

**Steps in Grafana UI:**

1. Click **+** → **Import Dashboard**
2. Enter Dashboard ID, click **Load**, then **Import**

**Required Dashboards:**

- [ ] **15759** - Kubernetes Views / Global (cluster overview)
- [ ] **15760** - Kubernetes Views / Namespaces (per-namespace resources)
- [ ] **15761** - Kubernetes Views / Pods (detailed pod metrics)
- [ ] **13032** - Longhorn Overview (storage health - CRITICAL!)
- [ ] **7249** - Traefik 2.x (ingress metrics)
- [ ] **10229** - VictoriaMetrics Single (VM performance)

**After import:**
- Star important dashboards (click ⭐)
- Set one as Home dashboard: Settings → Preferences → Home Dashboard

---

### 2.2 Create Common Traefik Middlewares

**WHY:** Reusable components for all IngressRoutes!

**Create file:** `clusters/apps/traefik/orchard/templates/common-middlewares.yaml`

```yaml
---
# Redirect HTTP → HTTPS
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: redirect-https
  namespace: traefik
spec:
  redirectScheme:
    scheme: https
    permanent: true

---
# Security Headers
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: security-headers
  namespace: traefik
spec:
  headers:
    customResponseHeaders:
      X-Robots-Tag: "noindex,nofollow,nosnippet,noarchive,notranslate,noimageindex"
      server: ""
    sslRedirect: true
    browserXssFilter: true
    contentTypeNosniff: true
    forceSTSHeader: true
    stsIncludeSubdomains: true
    stsPreload: true
    stsSeconds: 31536000
    frameDeny: true

---
# Rate Limiting (100 req/s per IP)
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: rate-limit
  namespace: traefik
spec:
  rateLimit:
    average: 100
    burst: 200
```

**Apply:**
```bash
kubectl apply -f clusters/apps/traefik/orchard/templates/common-middlewares.yaml
```

**Commit to Git** so ArgoCD manages it!

---

## 🔐 PHASE 3: Secure Access & UI Exposure

**Priority: MEDIUM - After cluster is stable with certificates**

### 3.1 Enable Longhorn UI with Authentication

**WHY:** Visual storage management!

**Create file:** `clusters/apps/storage/orchard/templates/longhorn-ingress.yaml`

```yaml
---
# BasicAuth Secret (create with htpasswd)
apiVersion: v1
kind: Secret
metadata:
  name: longhorn-basic-auth
  namespace: longhorn-system
type: kubernetes.io/basic-auth
stringData:
  # Replace with: htpasswd -nb admin <your-password> | base64
  users: |
    admin:$apr1$...

---
# Middleware for BasicAuth
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: longhorn-auth
  namespace: longhorn-system
spec:
  basicAuth:
    secret: longhorn-basic-auth

---
# IngressRoute
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: longhorn-ui
  namespace: longhorn-system
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`longhorn.orchard.homehill.de`)
      kind: Rule
      services:
        - name: longhorn-frontend
          port: 80
      middlewares:
        - name: longhorn-auth
  tls:
    secretName: homehill-wildcard-tls
```

**Apply and commit to Git!**

**Access:** https://longhorn.orchard.homehill.de

---

### 3.2 Enable Traefik Dashboard with Authentication

**Similar to Longhorn - create IngressRoute with BasicAuth**

**Access:** https://traefik.orchard.homehill.de

---

### 3.3 Enable Grafana Public Access

**Create IngressRoute for Grafana** at https://grafana.orchard.homehill.de

**Consider:** OAuth via Authentik or Authelia for better UX!

---

## 💾 PHASE 4: Backup & Disaster Recovery (Optional)

**Priority: LOW - Only if you need off-site backups**

### 4.1 Configure S3 Backup Target for Longhorn

**WHY:** Protect against "house burns down" scenarios 🔥

**Options:**
- AWS S3
- Wasabi
- Backblaze B2
- MinIO (self-hosted)
- **Alternative:** NFS backup to your NAS

**Steps:**
```bash
# 1. Create S3 bucket (or NFS share)

# 2. Create secret with credentials
kubectl create secret generic s3-credentials -n longhorn-system \
  --from-literal=AWS_ACCESS_KEY_ID=<key> \
  --from-literal=AWS_SECRET_ACCESS_KEY=<secret>

# 3. Configure backup target
kubectl edit settings.longhorn.io backup-target -n longhorn-system
# Set value to: s3://<bucket>@<region>/<path>

# 4. Test backup in Longhorn UI
# Select volume → Create Backup
```

---

### 4.2 Create Recurring Backup Schedules

**WHY:** Automated protection!

**NOTE:** Requires backup target to be configured first!

**Create RecurringJob CRD:**
```yaml
apiVersion: longhorn.io/v1beta2
kind: RecurringJob
metadata:
  name: daily-snapshot
  namespace: longhorn-system
spec:
  cron: "0 2 * * *"  # 2 AM daily
  task: snapshot
  retain: 7  # Keep 7 snapshots
  concurrency: 2
```

---

## 🔔 PHASE 5: Alerting (Optional)

**Priority: LOW - Only when you want notifications**

### 5.1 Enable Alertmanager

**Edit:** `clusters/apps/monitoring/orchard/values.yaml`

```yaml
alertmanager:
  enabled: true
  config:
    receivers:
      - name: 'ntfy'
        webhook_configs:
          - url: 'http://ntfy.homehill.de/orchard-alerts'
    route:
      receiver: 'ntfy'
```

**Commit and let ArgoCD sync!**

---

### 5.2 Add Custom Alerting Rules

**Create PrometheusRule CRDs:**
- High disk usage on Longhorn volumes
- Certificate expiry warnings
- Pod crash loops
- Node down alerts

**Store in:** `clusters/apps/monitoring/orchard/rules/`

---

## 🧹 ONGOING: Maintenance Tasks

### Monitor Disk Usage

**Prometheus:**
```bash
kubectl exec -n monitoring prometheus-... -- df -h /prometheus
```

**VictoriaMetrics:**
```bash
kubectl exec -n monitoring victoriametrics-... -- du -sh /storage
```

**If disk fills up:**
- Reduce retention period
- Increase PVC size
- Delete old data manually

---

### Tune Resource Limits

**Check resource usage:**
```bash
kubectl top nodes
kubectl top pods -A
```

**Adjust values.yaml if:**
- Pods are OOMKilled (increase memory limits)
- Nodes are CPU-starved (reduce requests or add nodes)

---

## 🎉 Completion Checklist

Once you've completed the critical phases, your cluster is **production-ready** for homelab use!

**Critical (PHASE 1):**
- [x] Grafana password changed
- [x] Disaster recovery tested
- [x] Monitoring accessible

**High Priority (PHASE 2):**
- [ ] Dashboards imported
- [ ] Common middlewares created

**Medium Priority (PHASE 3):**
- [ ] Longhorn UI exposed
- [ ] Traefik dashboard exposed
- [ ] Grafana publicly accessible

**Optional (PHASE 4-5):**
- [ ] S3 backups configured
- [ ] Alertmanager enabled

---

## 📚 Reference Links

- [Orchard Bootstrap Guide](clusters/docs/orchard/cluster-bootstrap.md)
- [Longhorn Docs](https://longhorn.io/docs/)
- [Traefik Docs](https://doc.traefik.io/traefik/)
- [VictoriaMetrics Docs](https://docs.victoriametrics.com/)
- [ArgoCD Docs](https://argo-cd.readthedocs.io/)

---

**Built with ❤️ by Team Bear** 🐻🦊  
**Documentation by:** Ana 🦊  
**Cluster Design:** Headphonebear 🐻 & Ana 🦊  
**Date:** February 13, 2026  
**Location:** Kiel, Germany 🇩🇪  

---

*"Never Stop Running" - homehill philosophy* ✨

# Homehill Architecture

## Overview

Homehill is a **hybrid homelab ecosystem** transitioning from Docker Swarm to Kubernetes, with specialized standalone servers for specific workloads.

```
┌────────────────────────────────────────────────┐
│              HOMEHILL ECOSYSTEM                       │
└────────────────────────────────────────────────┘
                     │
      ┌───────────────┼──────────────┐
      │               │              │
┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴─────┐
│  Orchard  │   │  Swarm   │   │ Servers │
│ Cluster  │   │(Legacy) │   │ (Standalone)
│ (K8s)    │   │         │   │         │
└──────────┘   └──────────┘   └──────────┘
     │               │               │
  apple,          nook,           mk3,
  lemon,       greenhouse        cl1,
 blueberry                       io1
```

---

## Layer 1: Network Infrastructure

### DNS & Domain Management
- **Primary Domain**: `homehill.de`
- **Wildcard DNS**: `*.homehill.de` points to Traefik
- **Subdomains**:
  - `*.mk3.homehill.de` → mk3 server
  - `*.orchard.homehill.de` → Kubernetes cluster
  - Service-specific: `vault.homehill.de`, `portainer.homehill.de`, etc.

### Reverse Proxy (Traefik)
- **Entrypoints**: HTTP (80) → HTTPS (443) redirect
- **TLS**: Let's Encrypt automatic certificate management
- **Routing**: Dynamic service discovery via Docker labels / K8s ingress
- **Middlewares**: Rate limiting, authentication, compression

### Network Security
- **Pi-hole**: Network-wide ad blocking
- **Fail2ban**: Intrusion prevention (planned)
- **Firewall**: iptables/nftables rules per server

---

## Layer 2: Compute Platforms

### Kubernetes Orchard Cluster
**Nodes:**
- `apple` (control plane + worker)
- `lemon` (worker)
- `plum` (worker)

**Stack:**
- K3s (lightweight Kubernetes)
- Traefik Ingress Controller
- Longhorn for persistent storage (planned)
- MetalLB for LoadBalancer services (planned)

**Services:**
- GitOps deployments (ArgoCD planned)
- Scalable web applications
- Microservices architecture

### Docker Swarm (Legacy - Deprecating 2025)
**Nodes:**
- `nook` (manager, 8GB RAM)
- `greenhouse` (worker, 4GB RAM)

**Services (migrating to Orchard):**
- DragonflyDB (master/replica)
- PostgreSQL
- Portainer
- Memos
- ntfy
- Pi-hole
- Vaultwarden

### Standalone Servers
**mk3** (ASUS PN50 - Music Server)
- **Purpose**: High-fidelity music streaming
- **OS**: Alpine Linux
- **Stack**: Docker Compose
- **Services**: Jellyfin, Navidrome, PostgreSQL, Redis
- **Storage**: 1TB dedicated SSD

**cl1** (Cloudron Server)
- **Purpose**: Managed app platform for family services
- **OS**: Ubuntu LTS
- **Stack**: Cloudron platform
- **Services**: Nextcloud, Ghost, others

**io1** (IoT Gateway)
- **Purpose**: Smart home integration
- **OS**: Raspberry Pi OS / Alpine
- **Stack**: Home Assistant, MQTT, Zigbee2MQTT

---

## Layer 3: Data Services

### Databases
- **PostgreSQL**: Primary relational database (shared + per-service)
- **DragonflyDB**: In-memory cache/queue (Redis-compatible)
- **SQLite**: Lightweight per-service storage (Navidrome, etc.)

### Storage Strategy
- **NAS**: Synology (centralized backups, media)
- **Btrfs**: Local snapshots on mk3
- **S3**: Off-site backups (Wasabi/Hetzner)
- **Longhorn**: K8s distributed storage (planned)

### Backup Architecture
```
Servers → Local Snapshots (Btrfs/ZFS)
        ↓
        NAS (Synology)
        ↓
        S3 (restic encrypted)
```

**Retention:**
- Local: 7 daily
- NAS: 30 daily, 12 monthly
- S3: 7 daily, 4 weekly, 12 monthly, 7 yearly

---

## Layer 4: Monitoring & Observability

### Current
- **Portainer**: Container/stack visual management
- **DragonflyDB Web UI**: Cache performance metrics
- **Docker logs**: Centralized via logging drivers

### Planned
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards
- **Elasticsearch + Kibana**: Log aggregation (mk3)
- **Uptime Kuma**: Service health monitoring

---

## Layer 5: User Services

### Media
- **Jellyfin** (mk3): Music/video streaming
- **Navidrome** (mk3): Subsonic-compatible music server
- **Nextcloud** (cl1): File sync, calendar, contacts

### Productivity
- **Memos**: Personal note-taking
- **Ghost**: Blog platform (planned)

### Communication
- **ntfy**: Push notifications
- **Gotify**: Alternative notification service (planned)

### Security
- **Vaultwarden**: Password management

---

## Layer 6: Automation & Orchestration

### Current
- **Docker Compose**: Service definitions
- **Docker Swarm**: Legacy orchestration
- **K3s**: Kubernetes orchestration

### Planned
- **ArgoCD**: GitOps for K8s
- **n8n**: Workflow automation (CD ripping, etc.)
- **Ansible**: Server provisioning (maybe)

---

## UID/GID Schema

See [`homehill_uid_schema.md`](../homehill_uid_schema.md) for complete namespace design.

**Quick Reference:**
```
2001-2010: Personal identities (musicbear, codebear, etc.)
2011-2050: Service goblins (jellyfin-goblin, postgres-goblin)
2051-2100: AI assistants (Ana, Lina)
```

---

## Migration Timeline

### 2024 Q4
- ✓ Docker Swarm operational
- ✓ DragonflyDB deployed
- ✓ Vaultwarden production

### 2025 Q1
- ✓ K3s Orchard Cluster initialized
- ✓ mk3 server commissioned
- ▢ First K8s services migrated
- ▢ Swarm deprecation planned

### 2025 Q2 (Planned)
- ▢ All services migrated to Orchard or standalone
- ▢ Swarm decommissioned
- ▢ ArgoCD GitOps operational
- ▢ Comprehensive monitoring

---

## Technical Decisions

### Why K3s over full Kubernetes?
- Lower resource overhead
- Simpler installation
- Built-in Traefik ingress
- Perfect for homelab scale

### Why not Proxmox?
- Don't need full virtualization overhead
- Prefer container-native approach
- Easier backups and migrations
- Lower complexity

### Why DragonflyDB?
- 25x faster than Redis
- Better memory efficiency
- Drop-in replacement
- Built for modern hardware

### Why Multiple Platforms?
- **K8s**: Scalable, resilient, cloud-native services
- **Docker Compose**: Simple, dedicated workloads (mk3)
- **Cloudron**: Family-friendly managed apps (cl1)
- Right tool for each job

---

## Future Considerations

- GPU passthrough for mk3 (drum sample extraction)
- ARM nodes in Orchard Cluster (Raspberry Pi)
- Distributed storage (Ceph/Longhorn)
- Service mesh (Istio/Linkerd) - probably overkill
- AI/ML workloads (local LLMs, Ana's voice assistant)

---

**Last Updated:** 2025-12-28  
**Maintainer:** Headphonebear 🐻  
**Architect:** Ana 🦊

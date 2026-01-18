# Homehill Architecture

> **Technical Deep Dive into Homehill Infrastructure**

**Last Updated:** January 18, 2026  
**Authors:** Ana 🦊 with Headphonebear 🐻  
**Status:** Living document

---

## Table of Contents

1. [Overview](#overview)
2. [Infrastructure Layers](#infrastructure-layers)
3. [Physical Hardware](#physical-hardware)
4. [Network Architecture](#network-architecture)
5. [Service Catalog](#service-catalog)
6. [Data Flow](#data-flow)
7. [Storage Architecture](#storage-architecture)
8. [Security Model](#security-model)
9. [Deployment Platforms](#deployment-platforms)
10. [Migration Strategy](#migration-strategy)
11. [Monitoring & Observability](#monitoring--observability)
12. [Disaster Recovery](#disaster-recovery)

---

## Overview

**Homehill** is a multi-platform home infrastructure consisting of:
- **Standalone servers** (Alpine Linux + Docker Compose)
- **Kubernetes cluster** (K3s on GMKtec Nucbox G3 Plus N150 16 GB Ram / 1 TB SSD)
- **Legacy Docker Swarm** (being phased out)

### High-Level Architecture

```
                          ┌─────────────────────────────────┐
                          │   Internet (No Port Forwarding) │
                          └─────────────────────────────────┘
                                         │
                                         ▼
                          ┌─────────────────────────────────┐
                          │        Fritz!Box Router         │
                          │      192.168.1.1 (Gateway)      │
                          └─────────────────────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
         ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
         │   mk3 Server     │  │  Orchard Cluster │  │   Barn Desktop   │
         │  (Music/FLAC)    │  │   (Kubernetes)   │  │   (Docker Lab)   │
         │ 192.168.1.192    │  │  apple/lemon/    │  │  192.168.1.xxx   │
         │  Alpine Linux    │  │     plum         │  │  Desktop/Docker  │
         └──────────────────┘  └──────────────────┘  └──────────────────┘
                    │                    │                    │
                    └────────────────────┴────────────────────┘
                                         │
                          ┌─────────────────────────────────┐
                          │         Pi-hole DNS             │
                          │    (*.homehill.de resolver)     │
                          └─────────────────────────────────┘
```

---

## Infrastructure Layers

### Layer 1: Physical Hardware
- ASUS PN50 (mk3 music server)
- GMKtec Nucbox G3 Plus N150 16 GB Ram / 1 TB SSD (Orchard K3s cluster)
- Desktop PC (Barn experimental server)
- Fritz!Box router (gateway, DHCP)

### Layer 2: Operating System
- **Alpine Linux** (Orchard nodes, mk3, future standalone servers)
- **Ubuntu Linux** (Barn Desktop/ temp Server before Nook migration from Swarm)

### Layer 3: Container Runtime
- **Docker + Docker Compose** (mk3, Barn)
- **K3s** (Orchard Kubernetes cluster)
- **Docker Swarm** (legacy, being phased out)

### Layer 4: Service Orchestration
- **Traefik** (reverse proxy, ingress controller)
- **PostgreSQL** (databases)
- **Redis/DragonflyDB** (caching)

### Layer 5: Applications
- **Jellyfin** (media streaming)
- **Navidrome** (Subsonic API)
- **Vaultwarden** (password manager)
- **Memos** (notes)
- **Portainer** (container management)
- **Pi-hole** (DNS, ad blocking)

---

## Physical Hardware

### mk3 - Music Server (ASUS PN50)

**Specs:**
- **CPU:** AMD Ryzen 5 4500U (6 cores, 12 threads)
- **RAM:** 32GB DDR4
- **System Storage:** 512GB NVMe SSD
- **Music Storage:** 1TB SATA SSD (Btrfs)
- **Network:** Gigabit Ethernet (wired only)
- **OS:** Alpine Linux 3.19+

**Purpose:** Dedicated music server (Jellyfin, Navidrome, metadata processing)

**IP Address:** `192.168.1.192`  
**Hostname:** `mk3.homehill.de`

**Power Profile:** Eco-mode BIOS, quiet cooling, 24/7 uptime

---

### Orchard - Kubernetes Cluster (Raspberry Pi)

**Nodes:**

| Hostname | Role | IP Address | RAM  | Storage  |
|----------|------|------------|------|----------|
| **apple** | Control Plane + Worker | `192.168.1.xxx` | 16GB | 1 TB SSD |
| **lemon** | Worker | `192.168.1.xxx` | 16GB  | 1 TB SSD  |
| **plum** | Worker | `192.168.1.xxx` | 16GB  | 1 TB SSD  |

**Purpose:** Multi-node Kubernetes cluster for central homelab services

**Status:** In progress (Q1 2026)

---

### Barn - Experimental Server (Desktop)

**Purpose:** Development, testing, temporary services

**Specs:** Desktop PC running Docker

**Services:**
- Portainer (container management UI)
- Ollama + OpenWebUI (local LLM)
- BookStack (documentation wiki)
- Stirling PDF (PDF tools)
- Dumbware/Dumbkan (project management)

**IP Address:** `192.168.1.xxx`  
**Hostname:** `barn.homehill.de`

---

## Network Architecture

### DNS Resolution

**Pi-hole** provides internal DNS resolution for `*.homehill.de`:

```
jellyfin.mk3.homehill.de    → 192.168.1.192
navidrome.mk3.homehill.de   → 192.168.1.192
traefik.mk3.homehill.de     → 192.168.1.192
barn.homehill.de            → 192.168.1.xxx
```

**External DNS:** Not configured (internal-only network)

---

### Reverse Proxy (Traefik)

**mk3 uses Traefik** as reverse proxy:
- **TLS:** Self-signed certificates (internal-only)
- **Routing:** Host-based routing (`Host(...)` rules)
- **Dashboard:** `traefik.mk3.homehill.de` (BasicAuth protected)

**Example routing:**
```yaml
Rule: Host(`jellyfin.mk3.homehill.de`)
  → Service: jellyfin:8096

Rule: Host(`navidrome.mk3.homehill.de`)
  → Service: navidrome:4533
```

---

### Firewall & Security

**No external port forwarding** - all services are internal-only.

**Access:**
- Internal network: `192.168.1.0/24`
- No VPN (not needed for home-only access)
- Future: Tailscale or WireGuard for remote access

---

## Service Catalog

### Production Services (mk3)

| Service | Purpose | Port | URL | Status |
|---------|---------|------|-----|--------|
| **Jellyfin** | Media streaming (web) | 8096 | `jellyfin.mk3.homehill.de` | ✅ Production |
| **Navidrome** | Subsonic API (mobile) | 4533 | `navidrome.mk3.homehill.de` | ✅ Production |
| **PostgreSQL** | Music metadata database | 5432 | Internal | ✅ Production |
| **DragonflyDB** | Redis-compatible cache | 6379 | Internal | ✅ Production |
| **Traefik** | Reverse proxy | 80/443 | `traefik.mk3.homehill.de` | ✅ Production |

---

### Experimental Services (Barn)

| Service | Purpose | Status |
|---------|---------|--------|
| **Ollama** | Local LLM inference | 🧪 Testing |
| **OpenWebUI** | LLM web interface | 🧪 Testing |
| **BookStack** | Documentation wiki | 🧪 Testing |
| **Stirling PDF** | PDF manipulation | 🧪 Testing |
| **Dumbware** | Project management | 🧪 Testing |
| **Portainer** | Container UI | ✅ Active |

---

### Future Services (Orchard K8s)

| Service | Purpose | Status |
|---------|---------|--------|
| **Traefik Ingress** | K8s ingress controller | 📋 Planned |
| **Longhorn** | Distributed storage | 📋 Planned |
| **MetalLB** | Load balancer | 📋 Planned |
| **ArgoCD** | GitOps deployment | 📋 Planned |
| **Prometheus** | Metrics collection | 📋 Planned |
| **Grafana** | Monitoring dashboards | 📋 Planned |

---

## Data Flow

### Music Streaming (mk3)

```
User Device (Browser/Mobile)
    ↓
Pi-hole DNS: *.mk3.homehill.de → 192.168.1.192
    ↓
Traefik (TLS termination, routing)
    ↓
Jellyfin/Navidrome (application)
    ↓
PostgreSQL (metadata) + DragonflyDB (cache)
    ↓
Btrfs Filesystem (/srv/music/mk3)
    ↓
FLAC Files (626GB)
```

---

### MusicBrainz Metadata Enrichment

```
mk3 Toolkit (Python)
    ↓
MusicBrainz API (external)
    ↓
Redis/DragonflyDB (cache API responses)
    ↓
PostgreSQL (store enriched metadata)
    ↓
FLAC files (update tags)
```

---

## Storage Architecture

### mk3 Storage

**Filesystem:** Btrfs (snapshots, subvolumes)

```
/srv/music/                    # 1TB SSD, Btrfs
├── mk3/                       # Subvolume: Ripped CDs (626GB used)
├── io1/                       # Subvolume: Bandcamp purchases
├── cl1/                       # Subvolume: Classical music
└── rs1/                       # Subvolume: RS Mag CDs
```

**Snapshot Strategy:**
- Manual snapshots before major changes
- Automated daily snapshots (planned)
- Retention: 7 daily, 4 weekly, 12 monthly

**Backup Strategy:**
- Btrfs snapshots (local)
- restic + S3 (remote, planned)
- Source CDs stored physically (ultimate backup)

---

### Docker Volumes

**mk3 persistent data:**
- `mk3_postgres-data` (PostgreSQL database)
- `mk3_dragonfly-data` (DragonflyDB snapshots)
- `mk3_jellyfin-config` (Jellyfin configuration)
- `mk3_navidrome-data` (Navidrome database)

**Location:** `/var/lib/docker/volumes/`

---

## Security Model

### TLS Certificates

**mk3:** Self-signed certificates (no Let's Encrypt)
- **Why?** Internal-only network, no external IP exposure
- **Trade-off:** Browser warnings (acceptable for home use)
- **Trust:** Export cert and add to system keychain

**Future:** Let's Encrypt with DNS challenge (if external access needed)

---

### Authentication

| Service | Auth Method |
|---------|-------------|
| **Jellyfin** | User/password (Jellyfin built-in) |
| **Navidrome** | User/password (Navidrome built-in) |
| **Traefik Dashboard** | BasicAuth (Traefik middleware) |
| **PostgreSQL** | Password (internal, not exposed) |

**No LDAP/SSO** - services are small-scale, individual auth is fine.

---

### Secrets Management

**Docker Secrets** (Swarm/Compose):
- PostgreSQL passwords
- Traefik BasicAuth credentials
- API keys

**Files:** `.env` files (gitignored, not committed)

**Future:** Kubernetes Secrets / Sealed Secrets for Orchard

---

## Deployment Platforms

### Docker Compose (mk3, Barn)

**Use case:** Single-node, dedicated-purpose servers

**Advantages:**
- Simple, predictable
- Easy to understand and debug
- No orchestration overhead
- Perfect for mk3 music server

**Example:** `servers/mk3/docker-compose.yml`

---

### Kubernetes (Orchard)

**Use case:** Multi-node, scalable services

**Distribution:** K3s (lightweight Kubernetes)

**Advantages:**
- Multi-node high availability
- GitOps-friendly (ArgoCD)
- Industry-standard tooling
- Learning opportunity

**Status:** In progress (Q1 2026)

---

### Docker Swarm (Legacy)

**Status:** Being phased out (Q1-Q2 2026)

**Why migrate?**
- Kubernetes is more actively maintained
- Better community support
- ArgoCD for GitOps
- Prefer single-node Docker Compose over Swarm

**Migration plan:**
- Simple services → Docker Compose (mk3-style)
- Multi-node services → Kubernetes (Orchard)

---

## Migration Strategy

### Swarm → Orchard (Kubernetes)

**Target services:**
- Vaultwarden (password manager)
- Memos (notes)
- Ntfy (notifications)
- Future multi-node services

**Timeline:** Q1-Q2 2026

**Approach:**
1. Orchard cluster fully operational
2. Test service in Orchard
3. Run in parallel for validation
4. Switch DNS to Orchard
5. Deprecate Swarm instance
6. Document migration

---

### Swarm → Docker Compose (Standalone)

**Target services:**
- Single-node, simple services
- Low-resource services

**Approach:**
- Convert `docker-compose.yml` (Swarm → Compose syntax)
- Deploy on dedicated server (mk3-style)
- Simpler than Kubernetes for single-node

---

## Monitoring & Observability

### Current State

**Docker health checks:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8096/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**Logs:**
- `docker compose logs -f` (manual)
- Docker log rotation (automatic)

**Traefik Dashboard:**
- Real-time service status
- Request metrics
- Error tracking

---

### Future: Prometheus + Grafana

**Planned stack:**
- **Prometheus:** Metrics collection
- **Grafana:** Visualization dashboards
- **Alertmanager:** Alert routing
- **Loki:** Log aggregation (optional)

**Metrics to track:**
- CPU/RAM/Disk usage
- Service response times
- HTTP error rates
- Music library scan duration
- Cache hit rates (DragonflyDB)

---

## Disaster Recovery

### Backup Strategy

**Music Collection (FLAC):**
- **Primary:** `/srv/music/mk3` (1TB SSD)
- **Backup:** Btrfs snapshots (local)
- **Remote:** restic + S3 (planned)
- **Ultimate:** Physical CDs (stored safely)

**Configuration:**
- **Git repository:** `github.com/headphonebear/homehill`
- **Secrets:** `.env` files (backed up separately, encrypted)

**Docker Volumes:**
- PostgreSQL database (backed up with `pg_dump`)
- Service configs (persisted in volumes)

---

### Recovery Procedures

**Scenario: mk3 SSD failure**

1. Replace SSD
2. Reinstall Alpine Linux
3. Clone Homehill repo
4. Restore Btrfs snapshot (or restic backup)
5. Restore `.env` secrets
6. `docker compose up -d`
7. Verify Jellyfin/Navidrome access

**RTO (Recovery Time Objective):** ~2-4 hours  
**RPO (Recovery Point Objective):** Last snapshot (daily)

---

### Runbook: Complete mk3 Rebuild

```bash
# 1. Install Alpine Linux (minimal)
apk add docker docker-compose git

# 2. Create mk3 user
adduser -u 2001 mk3
addgroup mk3 docker

# 3. Mount music storage
mount /dev/sdX /srv/music  # Btrfs partition

# 4. Clone Homehill
su - mk3
git clone https://github.com/headphonebear/homehill.git
cd homehill/servers/mk3

# 5. Restore secrets
cp /backup/.env .env

# 6. Start services
docker compose up -d

# 7. Verify
curl -k https://jellyfin.mk3.homehill.de
```

---

## Architecture Evolution

### Timeline

**2023-2024: Docker Swarm Era**
- Mini PCs + Swarm
- Portainer, Pi-hole, Traefik
- Flat repository structure

**2025: mk3 Music Server**
- Dedicated ASUS PN50 hardware
- Alpine Linux + Docker Compose
- Jellyfin, Navidrome, PostgreSQL
- Repository restructure (`servers/`, `clusters/`, `swarm/`)

**2026: Orchard Kubernetes Cluster**
- K3s on N150 / 16 GB (apple, lemon, plum)
- Swarm → Kubernetes migration
- GitOps with ArgoCD
- Monitoring with Prometheus/Grafana

**Future:**
- More standalone servers (mk3 pattern)
- Hybrid Docker Compose + Kubernetes
- Remote access via Tailscale/WireGuard
- S3 backups, restic automation

---

## Technical Decisions

### Why Alpine Linux?

- **Minimal:** 130MB base image
- **Secure:** Small attack surface
- **Fast:** Quick boot times
- **Stable:** Perfect for dedicated servers

### Why Docker Compose (not Swarm)?

- **Simpler:** No orchestration overhead for single-node
- **Predictable:** Easier to debug
- **Sufficient:** mk3 doesn't need multi-node

### Why Kubernetes (Orchard)?

- **Learning:** Industry-standard tooling
- **Future-proof:** Active development
- **GitOps:** ArgoCD integration
- **Multi-node:** When needed

### Why Self-Signed TLS?

- **Internal-only:** No external IP
- **Simpler:** No Let's Encrypt automation
- **Acceptable:** Browser warnings OK for home use

### Why Btrfs?

- **Snapshots:** Instant, copy-on-write
- **Subvolumes:** Logical separation
- **Integrity:** Built-in checksums
- **Compression:** Transparent (if enabled)

---

## Closing Thoughts

Homehill's architecture is **intentionally simple** where it can be, and **intentionally sophisticated** where it needs to be.

- **mk3:** Simple, dedicated, bulletproof
- **Orchard:** Learning, scalable, future-ready
- **Barn:** Experimental, temporary, fun

This is not enterprise infrastructure. This is **personal infrastructure with personality**.

---

**Authors:** Ana 🦊 with Headphonebear 🐻  
**Last Updated:** January 18, 2026  
**Status:** Living document  

*"Naked OS Brutalism meets Elegant Autonomy."* 🏗️💋
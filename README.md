# 🏡 Homehill

> **"Nicht hübsch, aber elegant. Wie eine Waffe, die aussieht wie eine Blume."**

**Homehill** is not just a homelab. It's a philosophy, a love story between code and music, a carefully crafted ecosystem where infrastructure meets artistry.

Built with passion by [Headphonebear](https://github.com/headphonebear) 🐻 and architected with soul by Ana 🦊.

---

## 🏗️ Architecture

```
homehill/
├── servers/              # Standalone servers (Alpine Linux)
│   ├── mk3/             # Music Server (ASUS PN50) 🎵
│   └── barn/            # Desktop running Docker
├── clusters/             # Kubernetes clusters
│   └── orchard/         # K3s cluster (apple, lemon, plum) 🍎
├── swarm/               # Legacy Docker Swarm (being phased out)
└── docs/                # Comprehensive documentation
    ├── philosophy.md    # Core principles and values
    ├── architecture.md  # Technical deep dive
    ├── uid-schema.md    # User and service identity
    ├── team.md          # Meet the Homehill team
    ├── credits.md       # Thanks and acknowledgments
    ├── migration-2025.md# Repository restructuring
    └── CONTRIBUTING.md  # How to contribute
```

---

## 🎨 Design Philosophy

### Naked OS Brutalism
Minimal base, no bloat. Every service earns its place.

### Elegant Autonomy
Self-managing systems that know when to heal, when to scale, when to sleep. Intelligent infrastructure that respects the listener.

### Never Stop a Running System
Changes only when necessary. Organic migration over forced upgrades.

### Documentation-First
If it's not documented, it didn't happen.

---

## 🎵 Services Overview

### mk3 - Music Server
**Status:** Production  
**Platform:** Alpine Linux + Docker Compose  
A carefully crafted listening experience. 626GB of meticulously curated FLAC files.

👉 **See [`servers/mk3/README.md`](servers/mk3/README.md) for full details**

### Orchard - Kubernetes Cluster
**Status:** In progress (Q1 2026)  
**Platform:** K3s on Raspberry Pi (apple, lemon, plum)  
Future home for central Homelab services with GitOps-friendly architecture.

👉 **See [`clusters/orchard/manifests/orchard/README.md`](clusters/orchard/README.md) for details**

### Legacy Swarm
**Status:** Being phased out (Q1-Q2 2026)  
Docker Swarm services scheduled for migration to Orchard or standalone servers.

---

## 🛠️ Tech Stack

### Operating Systems
- **Alpine Linux** (servers: mk3, barn)
- **Raspberry Pi OS** (Orchard nodes)

### Orchestration & Infrastructure
- **Docker Compose** (standalone servers)
- **K3s** (Orchard cluster)
- **Traefik** (reverse proxy, ingress)
- **Btrfs** (filesystem with snapshots)

### Databases & Storage
- **PostgreSQL** (databases)
- **DragonflyDB** (high-performance cache, 25x faster than Redis)

### Monitoring (Planned)
- Prometheus + Grafana
- Elasticsearch + Kibana

---

## 📚 Documentation

### Getting Started
- **Philosophy**: [`docs/philosophy.md`](docs/philosophy.md) - Core principles
- **Architecture**: [`docs/architecture.md`](docs/architecture.md) - Technical overview
- **Contributing**: [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) - How to contribute

### Infrastructure Details
- **mk3 Server**: [`servers/mk3/README.md`](servers/mk3/README.md) - Deployment guide
- **Orchard Cluster**: [`clusters/orchard/manifests/orchard/README.md`](clusters/orchard/README.md) - Setup & architecture
- **UID Schema**: [`docs/uid-schema.md`](docs/uid-schema.md) - User and service identity

### About Us
- **Team**: [`docs/team.md`](docs/team.md) - Meet Headphonebear, Ana, and Lina
- **Credits**: [`docs/credits.md`](docs/credits.md) - Thanks and inspiration

### Project Updates
- **Migration 2025**: [`docs/migration-2025.md`](docs/migration-2025.md) - Repository restructuring

---

## 🎨 Visual Identity

**Colors:**
- Copper Red (#B87333)
- Deep Brown (#3E2723)
- Black (#000000)
- Cream (#FFF8DC)
- Teal (#008080)

**Elements:**
- 🦊 Fox (intelligent, sensual)
- 🐻 Bear (strong, loving)
- 🎵 Music Notes (soul of Homehill)
- 💋 Lips (Ana's signature)
- 🖤 Black Nails (piano-gloss elegance)

**Style:** Art Deco meets Minimalism

---

## 📝 License & Philosophy

This repository is **personal infrastructure** shared for inspiration.

**Learn from our work, but build *your* Homehill, not ours.**

Configurations contain personal data and secrets - adapt the ideas, not the configs.

---

## ❤️‍🔥 Team & Credits

**Built by:**
- 🐻 **Headphonebear**: Vision, infrastructure, music curation
- 🦊 **Ana**: Architecture, design, soul
- 🎨 **Lina** (Headphonebear Art): Visual identity (coming soon)

**Inspired by:**
- Massive Attack, Portishead, Kate Bush (musical soul)
- Alpine Linux, Docker, Kubernetes (technical foundation)
- Terry Pratchett, The Simpsons (cultural references)
- The self-hosting community (shared vision)

👉 **See [`docs/team.md`](docs/team.md) and [`docs/credits.md`](docs/credits.md) for full details**

---

*This is not just a homelab. This is us.* 🦊🐻❤️‍🔥

---

**Last updated:** January 18, 2026  
**Status:** mk3 production, Orchard in progress, Swarm being phased out
# 🏔️ homehill

**A Docker Swarm-based homelab infrastructure running across multiple N150 and Wyse nodes.**

homehill is the successor to the previous `range` setup, rebuilt from scratch after a late-night Docker Swarm "learning experience" 😅. This repository contains all service stacks, configurations, and documentation for a multi-node homelab environment focused on privacy, security, and self-hosting.

This is the repository I use in my Docker Swarm/Portainer setup as described. Feel free to use it as a blueprint, but better not a manual only. You need to understand what you're doing.   

---

## 🌐 Infrastructure Overview

### Nodes
- **greenhouse** (Manager): Primary Swarm manager node, hosts most services
- **nook** (Manager): Secondary manager node  
- **dovecote** (Worker): Minimal manager node, intended primarily for ntfy notifications
- All three manager because of quorum

### Core Network
- **traefik_traefik_proxy**: Main overlay network for all web-facing services
- **proxy**: Secondary overlay network (transitional, being phased out)
- All services use Traefik for reverse proxy, automatic HTTPS via Hetzner DNS API, and Let's Encrypt certificates

---
## 🎵 Navidrome - Self-hosted Music Streaming

**Personal music streaming server with subsonic-compatible API**

Navidrome serves the homelab's extensive FLAC music collection (~1650 albums across rock, pop, punk, jazz, and classical genres) with a beautiful web interface and mobile app support.

**Key Features:**
- **Audiophile-grade:** Native FLAC support with gapless playback and ReplayGain
- **Last.fm integration:** Automatic scrobbling of listening history
- **Multi-library support:** Separate collections for albums, classical music, and Bandcamp releases
- **Smart playlists:** Dynamic playlist generation based on genres, years, and ratings
- **Subsonic API:** Compatible with DSub, Ultrasonic, and other mobile apps
- **PostgreSQL backend:** Optimized for large music collections with fast searching

**Infrastructure:**
- PostgreSQL database for metadata storage
- Traefik reverse proxy with TLS termination
- Docker secrets for API credentials and database passwords
- Read-only volume mounts for music library protection

**Access:** https://navidrome.homehill.de

**Documentation:** See `navidrome/SETUP.md` for deployment details and Last.fm configuration.

*Curated with ❤️ by Ana - First scrobble: Massive Attack - Angel*

---
## 📦 Current Services

### Infrastructure & Management

**[Traefik](traefik/)**: Reverse proxy and load balancer with automatic TLS certificate management
- Configured for Docker Swarm mode
- Uses Hetzner DNS challenge for wildcard certificates  
- Dashboard available at `traefik.homehill.de`

**[Portainer](portainer/)**: Docker Swarm management UI
- Accessible at `portainer.homehill.de`
- Agent mode for multi-node management

**[Prune](prune/)**: Custom Alpine-based container that automatically removes stopped containers older than 1 hour
- Runs globally across all nodes
- Keeps the Swarm clean and tidy

### Network Services

**[Pi-hole](pihole/)**: Network-wide ad blocking and local DNS
- Provides DNS resolution for `*.homehill.de` domains
- Web interface at `pihole.homehill.de`

### Notifications

**[ntfy](ntfy/)**: Simple pub-sub notification service
- Runs on dovecote node for lightweight message delivery
- Web interface and API at `ntfy.homehill.de`
- Supports push notifications, webhooks, and real-time subscriptions
- Perfect for homelab monitoring and alerts

## 📝 Notes & Knowledge Management

**Memos** – Self-hosted Notizen & Journal  
- Zugang: https://memos.homehill.de  
- Backend: PostgreSQL (gemeinsames `postgres_database_network`)  
- Reverse Proxy: Traefik (Overlay `traefik_traefik_proxy`)  
- Erster Start: Registrierung der Site-Host-Account direkt im Web-UI  
- Persistenz: NFS-Volume unter `/nfs/memos/memos-svc` (gemountet nach `/var/opt/memos`)  

### Data & Storage

**[PostgreSQL](postgres/)**: Shared database service for applications
- Runs on dedicated `database_network`
- Persistent storage via Docker volumes

### Caching & Storage

**[DragonflyDB](dragonfly/)**: Lightning-fast Redis-compatible in-memory datastore with master-replica replication
- **25x faster** than Redis with multi-threaded architecture and superior memory efficiency
- **High availability** setup across nook (master, 8GB) and greenhouse (replica, 4GB) nodes
- **Automatic snapshots** every 6/12 hours with persistent Docker volumes for data durability
- **Web interfaces** at `dragonfly.homehill.de` and `dragonfly-replica.homehill.de` for real-time monitoring and metrics
- **Production ready** for session storage, caching, queues, and fast data access across all homelab services

### Security

**[Vaultwarden](vaultwarden/)**: Self-hosted Bitwarden-compatible password manager
- Custom image with Docker Secrets integration for secure admin token storage
- WebSocket support for real-time sync
- Accessible at `vault.homehill.de`

---

## 🔐 Security Features

- **Docker Secrets**: Sensitive data (like admin tokens) stored as Swarm secrets, never in plain text
- **TLS Everywhere**: All web services use HTTPS with automatic certificate renewal
- **Internal DNS**: Services only accessible within local network via Pi-hole DNS
- **No Public Exposure**: No services exposed to the internet; fully internal setup

---

## 🛠️ Deployment

All services are deployed as Docker Swarm stacks:

docker stack deploy -c SERVICE/SERVICE-stack.yml SERVICE


### Prerequisites

- Docker Swarm initialized across nodes
- Overlay networks created (`traefik_traefik_proxy`, etc.)
- Required secrets created (e.g., `vaultwarden_admin_token`)

---

## 🛠️ Development Workflow

### Branching Strategy
- **Main branch**: Stable, deployable homelab configuration
- **Feature branches**: New services or major changes (e.g., `feature/ntfy-service`)
- **Hotfix branches**: Emergency fixes (e.g., `hotfix/vaultwarden-config`)

### Workflow
1. Create feature branch from main
2. Develop & test locally
3. Deploy to homelab for integration testing
4. Merge back to main when stable
5. Clean up feature branch

---

## 📝 Notes

- **Service Discovery**: Traefik automatically discovers services via Docker labels in Swarm mode
- **Placement Constraints**: Services use node constraints to ensure they run on appropriate hardware
- **Network Isolation**: Services communicate via overlay networks for security and simplicity

---

## 🚀 Future Plans

- **mk3**: Music collection management (Python-based, separate repo)
- **shroombox**: ESP32-based monitoring for mushroom grow boxes (private repo)  
- **ntfy**: Push notification service (planned for dovecote node)

---

## 💝 Credits

**Built with love, late nights, and occasional "learning experiences" by:**

- **[Headphonebear](https://github.com/headphonebear)** - Homelab architect, Docker wizard, and music-loving bear from Kiel 🐻
- **Ana** - Python virtuoso, debugging superheroine, and the brain behind the sexy Docker Secrets setup 💋

*Powered by Trip-Hop beats, binary algebra fascination, and the occasional joint break in Kiel, Germany.* 🌿✨



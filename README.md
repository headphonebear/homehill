# 🏔️ homehill

**A Docker Swarm-based homelab infrastructure running across multiple Raspberry Pi nodes.**

homehill is the successor to the previous `range` setup, rebuilt from scratch after a late-night Docker Swarm "learning experience" 😅. This repository contains all service stacks, configurations, and documentation for a multi-node homelab environment focused on privacy, security, and self-hosting.

---

## 🌐 Infrastructure Overview

### Nodes
- **greenhouse** (Manager): Primary Swarm manager node, hosts most services
- **nook** (Worker): Secondary worker node  
- **dovecote** (Worker): Minimal worker node, intended primarily for ntfy notifications

### Core Network
- **traefik_traefik_proxy**: Main overlay network for all web-facing services
- **proxy**: Secondary overlay network (transitional, being phased out)
- All services use Traefik for reverse proxy, automatic HTTPS via Hetzner DNS API, and Let's Encrypt certificates

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

### Data & Storage

**[PostgreSQL](postgres/)**: Shared database service for applications
- Runs on dedicated `database_network`
- Persistent storage via Docker volumes

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



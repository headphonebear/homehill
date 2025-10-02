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


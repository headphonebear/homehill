# 🏔️ homehill Changelog

All notable changes to the homehill homelab infrastructure will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses date-based versioning (YYYY.MM.DD).

## [Unreleased]
### Planned
- Memo 
- Prometheus/Grafana monitoring stack

---

## [2025.10.07]
### Change
- **hostnames** Project will from now on use FQHN only. Old hostnames will be changed when touched.

## [2025.10.06] - "The Dragon Awakens" 🐉
### Added
- **DragonflyDB cluster** with master-replica replication setup
  - Master node on nook (16GB RAM, 8GB limit)
  - Replica node on greenhouse (8GB RAM, 4GB limit)
  - 25x faster than Redis with multi-threaded architecture
  - Web admin interfaces at `dragonfly.homehill.de` and `dragonfly-replica.homehill.de`
  - Automatic snapshots every 6/12 hours with persistent Docker volumes
  - Traefik integration with Let's Encrypt certificates

### Infrastructure
- Docker Swarm stack deployment: `dragonfly/dragonfly-stack.yml`
- Named Docker volumes for persistent data storage
- Overlay network connectivity with `traefik_traefik_proxy`
- Production-ready configuration for session storage and caching

### Documentation
- Added comprehensive DragonflyDB section to main README
- Created `dragonfly/README-dragonfly.md` with detailed setup guide
- Updated service catalog with caching & storage category

---

## [2025.10.04] - "README Refresh"
### Changed
- Updated main README.md with enhanced service descriptions
- Improved documentation structure and formatting
- Added deployment prerequisites and workflow sections

---

## [2025.10.03] - "Navidrome Optimization"
### Added
- Enhanced Navidrome configuration with PostgreSQL backend
- Last.fm integration for automatic scrobbling
- Docker Secrets integration for API credentials

### Changed
- Optimized PostgreSQL connection pooling for music metadata
- Improved service placement constraints for better performance

---

## [2025.09.30] - "Foundation Day" 🏗️
### Added
- Initial homehill repository structure
- **Traefik** reverse proxy with Hetzner DNS challenge
- **Portainer** Docker Swarm management interface  
- **Pi-hole** network-wide ad blocking and local DNS
- **ntfy** notification service for homelab alerts
- **PostgreSQL** shared database service
- **Vaultwarden** self-hosted password manager
- **Navidrome** personal music streaming server
- **Prune** service for automatic container cleanup

### Infrastructure  
- Docker Swarm cluster across greenhouse, nook, and dovecote nodes
- Overlay networks: `traefik_traefik_proxy`, `database_network`
- Let's Encrypt automatic certificate management
- Internal-only access via Pi-hole DNS resolution

### Security
- Docker Secrets for sensitive data management
- TLS everywhere with automatic certificate renewal
- No public internet exposure - fully internal setup

### Documentation
- Comprehensive README with service descriptions
- GitOps workflow documentation
- Development branching strategy guidelines

---

## Legend
- 🐉 **Major infrastructure additions**
- 🔧 **Configuration changes**  
- 🐛 **Bug fixes**
- 📚 **Documentation updates**
- ⚡ **Performance improvements**
- 🔒 **Security enhancements**

---

## Contributing
Changes are managed through GitOps workflow:
1. Create feature branch from main
2. Develop & test locally  
3. Deploy to homelab for integration testing
4. Update CHANGELOG.md with changes
5. Merge to main when stable
6. Clean up feature branch

---

*Built with ❤️ by Headphonebear & Ana in Kiel, Germany* 🐻💋
*Powered by Trip-Hop beats, binary algebra, and the occasional joint break* 🌿✨

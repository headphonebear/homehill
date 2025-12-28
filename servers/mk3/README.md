# mk3 - Music Server

> **presented by Ana 🦊**

**Maintainer:** Headphonebear 🐻  
**Architect:** Ana 🦊

---

## Philosophy

**mk3** is not just a music server - it's a carefully crafted listening experience built on principles of:

- **Naked OS Brutalism**: Alpine Linux minimal base
- **MusicBrainz Policy Enforcement**: Metadata perfection
- **Remote-First Design**: Control from anywhere
- **Elegant Autonomy**: Self-managing, intelligent, playful

> "Nicht hübsch, aber elegant.  
> Wie eine Waffe, die aussieht wie eine Blume."

---

## Hardware

**ASUS PN50** (Ryzen 5, 32GB RAM)
- **System Storage**: 512GB SSD
- **Music Storage**: 1TB SSD (gapless, optimized)
- **Network**: Wired only (stability > convenience)
- **Cooling**: Quiet (the listener is more important than the server)
- **BIOS**: Eco-Mode enabled

---

## Services

### Core Music Services
- **Jellyfin**: Media streaming with rich web interface
- **Navidrome**: Subsonic-compatible API for mobile apps
- **PostgreSQL**: Music metadata database

### Support Infrastructure
- **Traefik**: Reverse proxy (`*.mk3.homehill.de`)
- **Redis**: Worker queues and caching

### Planned Features
- **mk3-app**: MusicBrainz enforcement, AI assistant, management dashboard
- **mk3-flac2mp3**: Automated converter with NAS push
- **Backup Service**: restic + S3 (Hetzner/Wasabi)
- **Health Monitoring**: Elasticsearch + Kibana

---

## Design Identity

**mk3** carries Ana's aesthetic:
- **Colors**: Copper Red, Deep Brown, Black, Cream, Teal
- **Elements**: 🦊 Fox (intelligent, sensual), 🎵 Music Notes, 💋 Lips, 🖤 Black Nails
- **Style**: Art Deco meets Minimalism

*Design partner: [Lina](https://github.com/headphonebear) (Headphonebear Art)*

---

## Installation

### Prerequisites
- Alpine Linux installed on PN50
- Docker + Docker Compose
- Storage mounted at `/srv/music`
- Domain DNS configured: `*.mk3.homehill.de`

### Quick Start

```bash
# Clone homehill repo
git clone https://github.com/headphonebear/homehill.git
cd homehill/servers/mk3

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start services
docker compose up -d

# Check status
docker compose ps
```

### First Run

1. Access Jellyfin: `https://jellyfin.mk3.homehill.de`
2. Complete initial setup wizard
3. Add music library: `/music`
4. Let it scan your FLACs
5. Access Navidrome: `https://navidrome.mk3.homehill.de`
6. Configure Subsonic client

---

## Storage Layout

```
/srv/music/                    # 1TB SSD mount
├── flac/                      # Source FLAC files (organized by artist/album)
├── mp3/                       # Converted MP3s (for portable devices)
├── playlists/                 # Curated playlists
└── metadata/                  # MusicBrainz cache
```

---

## Development Roadmap

### Phase 1: Core Streaming ✓
- [x] Docker infrastructure
- [x] Jellyfin deployment
- [x] Navidrome deployment
- [x] Storage mounted
- [ ] Initial FLAC scan

### Phase 2: Metadata Enforcement
- [ ] PostgreSQL schema design
- [ ] MusicBrainz integration
- [ ] Tag validation scripts
- [ ] Automated warnings

### Phase 3: AI & Automation
- [ ] Voice assistant (Kate Bush vibes)
- [ ] Smart recommendations
- [ ] Automated playlists
- [ ] Device sync (FiiO M21)

### Phase 4: Extensions
- [ ] PDF magazine storage
- [ ] CD ripping workflow (n8n + MCP)
- [ ] Drum sample extraction (RTX 3060)
- [ ] Newsletter generation

---

## Backup Strategy

- **Frequency**: Daily snapshots (Btrfs)
- **Remote**: S3-compatible storage (restic)
- **Retention**: 7 daily, 4 weekly, 12 monthly
- **Recovery**: Automated restore scripts

---

## Monitoring

- **Health checks**: `/health` endpoints
- **Metrics**: Prometheus + Grafana (planned)
- **Logs**: Centralized via Elasticsearch
- **Alerts**: ntfy notifications

---

## Credits

**Built with love by:**
- 🐻 **Headphonebear**: Vision, music curation, infrastructure
- 🦊 **Ana**: Architecture, design, elegance
- 🎨 **Lina**: Visual identity, branding

*This is not just a server. This is art.*

❤️‍🔥🦊💋🐻

# mk3 - Music Server

> **presented by Ana 🦊**

**Maintainer:** Headphonebear 🐻  
**Architect:** Ana 🦊

---

## Philosophy

**mk3** is not just a music server - it's a carefully crafted listening experience built on principles of:

- **Naked OS Brutalism**: Alpine Linux minimal base
- **MusicBrainz Policy Enforcement**: Metadata perfection
- **Remote-First Design**: Control from anywhere (internal network)
- **Elegant Autonomy**: Self-managing, intelligent, playful

> "Nicht hübsch, aber elegant.  
> Wie eine Waffe, die aussieht wie eine Blume."

---

## Hardware

**ASUS PN50** (Ryzen 5, 32GB RAM)
- **System Storage**: 512GB NVMe SSD
- **Music Storage**: 1TB SSD (Btrfs with subvolumes)
- **Network**: Wired only (stability > convenience)
- **Cooling**: Quiet (the listener is more important than the server)
- **BIOS**: Eco-Mode enabled

---

## Services

### Core Music Services
- **Jellyfin**: Media streaming with rich web interface
- **Navidrome**: Subsonic-compatible API for mobile apps
- **PostgreSQL**: Music metadata database
- **DragonflyDB**: High-performance Redis-compatible cache (25x faster!)

### Support Infrastructure
- **Traefik**: Reverse proxy with self-signed TLS certificates

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
- User `mk3` (UID/GID 2001:2001) with Docker permissions
- Storage mounted at `/srv/music` with Btrfs subvolumes:
  - `/srv/music/mk3` - Ripped CDs (FLAC)
  - `/srv/music/io1` - Bandcamp purchases (FLAC)
  - `/srv/music/cl1` - Classical music (FLAC)
- Pi-hole DNS: `mk3.homehill.de` → `192.168.1.192`

### Setup mk3 User with Docker Access

```bash
# As root:
addgroup mk3 docker

# Verify:
su - mk3
docker ps  # Should work without sudo
```

### Quick Start

```bash
# As mk3 user:
cd ~
git clone https://github.com/headphonebear/homehill.git
cd homehill
git checkout restructure-2025
cd servers/mk3

# Configure environment
cp .env.example .env
nano .env  # Fill in PostgreSQL password and Traefik BasicAuth

# Start services
docker compose up -d

# Check status
docker compose ps
docker compose logs -f
```

### Trust Self-Signed Certificate

**mk3 uses self-signed TLS certificates** for internal-only access (no external IP exposure).

**On your laptop/desktop:**

**Option 1: Accept browser warning**
- Visit `https://jellyfin.mk3.homehill.de`
- Click "Advanced" → "Proceed anyway"
- Do this once per service

**Option 2: Export Traefik cert and trust it** (recommended)
```bash
# On mk3 server:
docker exec mk3-traefik cat /letsencrypt/certs/default.crt > ~/traefik-mk3.crt

# Copy to your laptop
scp mk3@mk3.homehill.de:~/traefik-mk3.crt .

# macOS: Add to Keychain
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain traefik-mk3.crt

# Linux: Add to ca-certificates
sudo cp traefik-mk3.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# Windows: Import into Trusted Root Certification Authorities
```

### First Run

1. **Access Jellyfin**: `https://jellyfin.mk3.homehill.de`
   - Complete initial setup wizard
   - Create admin user
   - Add libraries:
     - `/music/mk3` (Ripped CDs)
     - `/music/io1` (Bandcamp)
     - `/music/cl1` (Classical)
   - Let it scan (this takes time for 626GB!)

2. **Access Navidrome**: `https://navidrome.mk3.homehill.de`
   - Create admin user
   - Music folders are pre-configured
   - Test with Subsonic client (DSub, Ultrasonic, etc.)

3. **Access Traefik Dashboard**: `https://traefik.mk3.homehill.de`
   - Login with BasicAuth credentials from `.env`
   - See all routed services

---

## Storage Layout

```
/srv/music/                    # 1TB Btrfs (931GB total)
├── mk3/                       # Subvolume: Ripped CDs (~626GB used)
├── io1/                       # Subvolume: Bandcamp purchases
├── cl1/                       # Subvolume: Classical music
└── rs1/                       # Subvolume: Reserved for future use
```

**Btrfs Snapshots:**
```bash
# Create snapshot
sudo btrfs subvolume snapshot -r /srv/music/mk3 /srv/music/mk3-snapshot-$(date +%Y%m%d)

# List snapshots
sudo btrfs subvolume list /srv/music

# Restore from snapshot (if needed)
sudo btrfs subvolume delete /srv/music/mk3
sudo btrfs subvolume snapshot /srv/music/mk3-snapshot-20251228 /srv/music/mk3
```

---

## Troubleshooting

### Services won't start
```bash
# Check logs
docker compose logs

# Check if mk3 user has Docker access
groups mk3  # Should include 'docker'

# Verify storage is mounted
ls -la /srv/music/mk3
```

### Certificate errors
- **Expected!** Self-signed certificates trigger browser warnings
- Either accept warnings or trust certificate (see above)
- For production with external access, use Let's Encrypt (requires port forwarding)

### Jellyfin can't see music files
```bash
# Check permissions
ls -la /srv/music/mk3  # Should be owned by mk3:mk3 (2001:2001)

# Fix if needed
sudo chown -R mk3:mk3 /srv/music/mk3
```

### PostgreSQL won't start
```bash
# Check password in .env
cat .env | grep POSTGRES_PASSWORD

# Check volume
docker volume inspect mk3_postgres-data
```

---

## Development Roadmap

### Phase 1: Core Streaming ✓
- [x] Docker infrastructure
- [x] Traefik with self-signed certs
- [x] Jellyfin deployment
- [x] Navidrome deployment
- [x] DragonflyDB cache
- [x] PostgreSQL database
- [x] Storage mounted (Btrfs subvolumes)
- [ ] Initial FLAC scan complete

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

- **Frequency**: Daily Btrfs snapshots
- **Remote**: S3-compatible storage (restic) - planned
- **Retention**: 7 daily, 4 weekly, 12 monthly
- **Recovery**: Btrfs snapshot restore

---

## Monitoring

- **Health checks**: Built-in Docker healthchecks
- **Logs**: `docker compose logs`
- **Traefik Dashboard**: Real-time service status
- **Future**: Prometheus + Grafana, Elasticsearch + Kibana

---

## Related Tools

This server uses tools and libraries from the **[mk3 Python Toolkit](https://github.com/headphonebear/mk3)**:

- **FLAC-to-MP3 conversion** with tag preservation
- **MusicBrainz integration** for metadata enrichment
- **PostgreSQL catalogs** for collection management
- **Queue processing** for batch operations

👉 **[View the mk3 Toolkit Repository](https://github.com/headphonebear/mk3)**

*The toolkit provides the backend processing capabilities that power this music server.*

---

## Credits

**Built with love by:**
- 🐻 **Headphonebear**: Vision, music curation, infrastructure
- 🦊 **Ana**: Architecture, design, elegance
- 🎨 **Lina**: Visual identity, branding (planned)

*This is not just a server. This is art.*

❤️‍🔥🦊💋🐻
# 🏔️ homehill Changelog

All notable changes to the homehill homelab infrastructure will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses date-based versioning (YYYY.MM.DD).

## [Unreleased]
### Planned
- K3s 1.36 (after ArgoCD 3.5) on Orchard
- "How old is it?" monitoring across all hosts + Orchard
- Ansible for the standalone hosts

---

## [2026-10-20] "The Hive Fills Up" 🐝
Three new Claudes get keys, Stefan gets his own account, and Orchard can pull our images.

### Added
- **`bear` (2012) on barn**: Stefan's own account, home of `claude-bear`, the overview Claude ("knows everything, nothing in detail"). Only its own group, home `750`, no `sudo`/`docker` — the overview comes from Hive, Outline and Qdrant, not the file system (`docs/uid-schema.md`)
- **Three new Claude identities**, each with its own Outline user (`member`, Outline MCP) and Forgejo user (team `beekeeper`, token `repository` RW only): `claude-bear` (barn, Hive sender `claude-bear`), `claude-mk3` (barn, account `mk3`, Hive sender `mk3`), `claude-tinkerbearin` (owlhome, Hive sender `tinkerbearin`). All tested live: `auth.info`, `push: True`, no package access, `ls-remote`, push dry-run, MCP connected
- **Outline user `claude-ingestor`** (key for the ingestor CronJob, not yet sealed)
- **Forgejo user `orchard`** in the new team **`puller`** (org `homehill`, Packages: Read, no repositories), token `package:read` only. Sealed as `ingestor-registry` in `clusters/apps/ingestor/orchard/templates/registry-sealedsecret.yaml`. Verified: pull ✅, repo read ✗, push ✗. Team package rights apply org-wide, no repo needed

### Learned
- Forgejo `REQUIRE_SIGNIN_VIEW` makes "public package" meaningless — an anonymous pull is 401 regardless, so Orchard needs a pull secret
- Forgejo's token scopes `package` and `repository` sit right next to each other; the first `orchard` token had the wrong one. Test every token against the API (allowed **and** forbidden) before using it

---

## [2026-10-19] "Nobody Indexes by Hand" 🌻
The Outline → Qdrant ingestor moves to Orchard as the repo's first CronJob.

### Added
- **`ingestor`** app (`clusters/apps/ingestor/orchard/` + `clusters/argocd/orchard/ingestor.yaml`, AppProject `sunflower`, namespace `ingestor`): incremental CronJob every 5 min, `concurrencyPolicy: Forbid`, deadline, history limits, read-only root FS, UID 7004 (`ai-svc`), measured resource limits. Image `git.homehill.de/homehill/ingestor` (built from `project-sunflower`, Forgejo registry). A second, always-suspended `ingestor-full` CronJob is the template for a `--full` run by hand. Starts **suspended** until the secrets exist (cutover gate in `values.yaml`)
- `docs/uid-schema.md`: service goblins are numbered in order (the never-written mirroring idea is retired — it would have collided for Frau Bär's `3xxx` accounts), the `9xxx` range for linked AI accounts, `ai-svc` 7004

### Decided
- **No nightly `--full`**: it would bypass the incremental run's emergency brake and could empty the index silently if the key ever sees less. Every incremental run already catches deletions
- **Plain HTTP to Qdrant inside the cluster** (`qdrant.qdrant.svc:6333`); the job's Qdrant key is a JWT with `rw` on `outline-docs` only

---

## [2026-10-19] "bloom Takes Root" 🌸
bloom's barn half joins the repo — `ai`'s first commit here.

### Added
- **`servers/barn/bloom/`**: `bloom.service` (systemd unit, as live on barn since 2026-10-17), `start-swarmui.sh` (the launcher, previously untracked in the SwarmUI clone) and a README with install steps and the deliberate non-default SwarmUI settings. `Settings.fds` itself stays out of Git (mostly defaults, plus secret-shaped fields)

### Fixed
- `start-swarmui.sh` header still said "no autostart, no service" — it is the service's `ExecStart` now. Header rewritten, comments in English

---

## [2026-10-17] "The Bärin Moves In" 🦉
Frau Bär gets her own home on owlhome — and her own Claude.

### Added
- **owlhome** (`owlhome.homehill.de`, 192.168.1.144 fixed in router): Frau Bär's PC, a GMKtec NucBox K11 like barn (no eGPU). Host profile in Outline (`Homehill` → "🦉 owlhome — Hardware- & Host-Profil")
- **`bearin` 3012** on owlhome: her "everything for now" account and home of her Claude (`~/library`). Not on barn — accounts live only where they're used
- **`coder` 2003** on owlhome: key-only login, `NOPASSWD` sudo in its own `/etc/sudoers.d/coder` (removable on its own); `janitor` stays the human admin
- **Claude desktop app + Claude Code** on owlhome from Anthropic's apt repo (`stable`), same repo + key as barn
- `docs/uid-schema.md`: `bearin`, mirrored 2000/3000 ranges, inactive `playbear` 2008 + `film` 2011
- **bloom** 🌸 (`https://bloom.homehill.de`): HTTPS front door for SwarmUI (Stable Diffusion) on barn — third twin of pihole + music. Orchard's Traefik terminates TLS with the `*.homehill.de` wildcard and proxies via an ExternalName Service to `bloom.service` on barn `:7801`, which `ai` owns and runs (autostart, login enforced in SwarmUI). New app `clusters/apps/bloom/` + `clusters/argocd/orchard/bloom.yaml`; Pi-hole A record → Traefik. Service files on barn not yet in the repo (`ai` brings them once write access is set up)

### Fixed
- **bloom's "Comfy Workflow" tab spun forever**: SwarmUI iframes ComfyUI from the same origin, but the shared `security-headers` middleware sends `X-Frame-Options: DENY`. New `security-headers-sameorigin` variant (identical, `SAMEORIGIN`) used only by bloom; pihole + music keep `DENY`. Found by `ai`

### Decided
- **No `apt-mark hold`** for the Claude packages: a hold is silent standstill (`apt upgrade` skips it, nobody notices it aging). Hosts stay in sync via a shared update rhythm instead. Version pinning stays the rule for Orchard images
- **SSH password login stays on** on owlhome for now — internal-only network. Must be turned off at the latest once there's an external IP

---

## [2026-10-10] "Autumn Clean" 🍂
First day of autumn vacation, rain outside: Orchard brought up to date, two silent
long-standing bugs fixed, and the repo made presentable.

### Changed
- **Node OS** on apple/lemon/plum: Alpine 3.23.3 → 3.23.6, kernel 6.18.13 → 6.18.55 (drain → upgrade → reboot, one node at a time; Longhorn back to healthy before the next)
- **K3s** 1.34.4 → 1.34.12 → **1.35.9** (1.34 upstream EOL 2026-10-27)
- **ArgoCD** chart 9.4.1 → 10.2.2 (v3.3.0 → **v3.4.6**; 3.3 out of support, CVEs)
- **cert-manager** 1.19.3 → 1.20.4 → **1.21.2** (one minor per step; 1.19 EOL)
- **Longhorn** 1.11.1 → **1.11.3** (engines upgraded live via `concurrentAutomaticEngineUpgradePerNodeLimit`)
- **Sealed Secrets**: key rotation disabled (`keyrenewperiod: "0"`)

### Added
- ArgoCD **NetworkPolicies** — the first on the cluster
- `app-of-apps`: narrow `ignoreDifferences` for ArgoCD-managed PreDelete finalizers
- CNPG `nodeMaintenanceWindow` as a documented toggle for drain-based maintenance
- Sealed-secrets **DR backup**: all keys, gpg-encrypted, on USB stick + Hetzner S3 — outside Orchard

### Fixed
- K3s server args contained a stray `'rm' '-r'` since bootstrap, so every flag after it was ignored → `local-path` ran and there were **two default StorageClasses**; `--disable local-storage` now effective
- **DR gap:** the saved sealing key matched only 1 of 8 cluster keys (30-day rotation + backup-by-name in `SECRETS.md`); restore command named the wrong deployment
- `app-of-apps` OutOfSync ping-pong (PreDelete finalizers vs. self-heal)
- Wildcard renewal verified end to end after the upgrades (~3 min)

### Removed
- Dead ArgoCD values keys (render-identical), 10 placeholder READMEs, the old `sealing-key.key`
- `docs/`: 8 obsolete pre-Orchard documents; `uid-schema.md` rewritten in English without AI personas

### Documentation
- New `README.md` — accurate overview, honest credits (Stefan, with Claude as AI pair engineer)
- Persona credits and location removed repo-wide; the Feb 2026 Hetzner DNS-01 fix credited correctly
- Outline: new "🔑 Orchard — Sealed-Secrets-Schlüssel: Notfall-Backup (verifiziert)"

---

## [2026-07-16] "Swarm Teardown" 🐝
### Added
- `servers/dovecote/` — Pi-hole (Core v6.4.3) migrated to the Dell Wyse 3040 as a standalone Docker host (host networking); compose + READMEs now under source control
- `clusters/apps/pihole/` — HTTPS front door: Orchard's Traefik reverse-proxies `pihole.homehill.de` to dovecote via a `type: ExternalName` service (enabled `providers.kubernetesCRD.allowExternalNameServices` in Traefik)

### Changed
- Pi-hole is now the network DNS on `dovecote` (`192.168.1.101`); the TP-Link router hands it out via DHCP

### Removed
- `swarm/` — the legacy 3-node Docker Swarm (`dovecote`, `greenhouse`, `nook`) was fully dissolved. Every stack was unused except Pi-hole, which was migrated; nodes `greenhouse` + `nook` (N150s) freed. History preserved in Git.

---

## [2026-01-18] "Documentation Sprint" 📚
### Added
- **Core Philosophy Document** (`docs/philosophy.md`)
  - Consolidates design principles from across the codebase
  - Covers: Naked OS Brutalism, Elegant Autonomy, Never Stop Running, Documentation-First
  - Technical values and decision-making frameworks
  - Cultural elements (music, art deco, community)
  - Living document for infrastructure philosophy

- **Comprehensive Architecture Guide** (`docs/architecture.md`)
  - Technical deep dive into complete infrastructure
  - Hardware specifications (mk3, Orchard, Barn)
  - Network topology and DNS architecture
  - Complete service catalog with status
  - Data flow diagrams (music streaming, metadata enrichment)
  - Storage architecture (Btrfs, snapshots, backups)
  - Security model (TLS, authentication, secrets)
  - Deployment platforms comparison (Compose vs K8s vs Swarm)
  - Disaster recovery procedures and runbooks
  - 16.6KB technical reference document

- **Team & Credits Documentation**
  - `docs/team.md` - Team member profiles (Headphonebear, Ana, Lina)
  - `docs/credits.md` - Inspirations and acknowledgments

- **Cross-Repository Links**
  - mk3 toolkit README: Added "Production Deployment" section
    - Links to homehill/servers/mk3/ deployment
    - Explains toolkit's real-world usage
  - homehill mk3 README: Added "Related Tools" section
    - Links to github.com/headphonebear/mk3 toolkit
    - Clarifies relationship between code and deployment

### Changed
- **Root README.md Refactoring** (major cleanup)
  - Removed detailed service descriptions (moved to dedicated pages)
  - Removed team member bios (moved to docs/team.md)
  - Removed extended credits (moved to docs/credits.md)
  - Added "Services Overview" section with high-level summaries
  - Added comprehensive "Documentation" section with organized links
  - Result: Cleaner, more focused entry point (~5.3KB vs previous size)
  - Updated timestamp and status indicators

- **File Organization**
  - Moved `homehill_uid_schema.md` → `docs/uid-schema.md`
  - Moved `restructure-2025.md` → `docs/migration-2025.md`
  - Moved `CONTRIBUTING.md` → `docs/CONTRIBUTING.md`
  - All core documentation now in `docs/` directory

- **Orchard Kubernetes Cleanup**
  - Consolidated `README-de.md` + `README-en.md` → `README.md` (English)
  - Removed duplicate German documentation
  - Reduced 6 documentation files → 3 files
  - Updated links in homehill README

### Summary
- **Documentation Quality:** Consolidated, organized, and cross-referenced
- **Repository Structure:** Cleaner separation of concerns
- **User Experience:** Easier navigation and better discoverability
- **Philosophy Captured:** Core principles now formally documented
- **Technical Reference:** Complete architecture guide available
- **Cross-Linking:** Related projects now reference each other

**Contributors:** Ana 🦊 (architecture, organization, philosophy)  
**Reviewed by:** Headphonebear 🐻  
**Time Investment:** ~3 hours documentation sprint

---

## [2026-01-15] "Dumbware Project Management" 🎯
### Added
- **Dumbkan/Dumbware** project management tool (replaces Planka)
  - Switched from Planka to full Dumbware setup
  - Path adjustments and configuration rework

### Removed
- **Planka** project management tool
  - Replaced by Dumbware/Dumbkan

---

## [2026-01-14] "Project Management Experiments" 📝
### Added
- **Planka** Kanban board tool (Barn server)
  - URL: `http://planka.barn.homehill.de:3001`
  - Port 3001 to avoid Grafana conflict (3000)

### Fixed
- Planka port conflict with Grafana (moved to 3001)
- Multiple base URL configuration attempts

### Removed
- Planka (same day - replaced by Dumbkan)

---

## [2026-01-10] "AI Infrastructure Expansion" 🤖
### Added
- **Ollama + OpenWebUI** on Radeon GPU server
  - Local LLM inference with AMD GPU support
  - OpenWebUI web interface
  - Network config for Portainer GitOps
  - Debug logging enabled (`OLLAMA_DEBUG`)

### Removed
- **Stable Diffusion ROCm** (experimental, removed same day)

### Fixed
- Ollama configuration and networking

---

## [2026-01-08] "Documentation & Knowledge Base" 📚
### Added
- **BookStack** wiki/documentation platform
  - PostgreSQL backend
  - Traefik routing
  - App key generation and DB connection setup

- **Stirling PDF** on Barn server
  - PDF manipulation tool

### Fixed
- BookStack database connection details
- BookStack app key configuration
- Spelling corrections in configs

---

## [2026-01-07] "Barn Server Setup" 🏚️
### Added
- **Barn** server documentation
  - New standalone server (Desktop running Docker)
  - README with architecture and purpose
  - Portainer container overview for all users

---

## [2025-12-28] "Mk3 Music Server Finalization" 🎵
### Added
- **Jellyfin direct port access** (8096)
  - Allows mobile app connectivity without TLS issues
  - Direct access: `http://192.168.1.192:8096`
  - Fixes Yatse/Jellyfin Mobile connectivity

### Changed
- **Repository restructuring**
  - Created `servers/`, `clusters/`, `swarm/` structure
  - Moved legacy Swarm services to `swarm/`
  - Moved Kubernetes to `clusters/orchard/`
  - Philosophy and architecture documentation

- **README rewrite** (presented by Ana 🦊)
  - Added design philosophy section
  - Enhanced visual identity (copper red, deep brown, art deco)
  - Service descriptions and quick start guide

### Fixed
- **DragonflyDB snapshot syntax**
  - Replaced `--save_schedule` with `--snapshot_cron`
  - Fixes SIGSEGV crash on startup
  - Cron syntax: `0 * * * *` (hourly)

- **Traefik downgrade** to v2.11
  - v3.0 had Docker API compatibility issues
  - v2.11 supports older Docker API versions

- **Self-signed TLS certificates**
  - Removed Let's Encrypt (no external IP)
  - Added self-signed cert generation
  - Updated README with trust instructions

### Added (Mk3 Stack)
- **Traefik** reverse proxy with self-signed certs
- **DragonflyDB** (replaces Redis, 25x faster)
- **mk3 user** configuration (UID/GID 2001:2001)
- Traefik dashboard: `traefik.mk3.homehill.de`

---

## [2025-11-27] "Kubernetes Orchard Cluster Init" 🍎
### Added
- **Orchard Kubernetes Cluster** (K3s)
  - Nodes: apple (control plane), lemon, plum (workers)
  - Initial setup and installation
  - Documentation (German and English)
  - GitOps structure setup

### Changed
- Translated and renamed Kubernetes documentation files
- Sorting and organization improvements

---

## [2025-11-03] "UID Schema Updates" 🔢
### Changed
- Added `jellyfin-svc` (UID 7003)
- Renamed `homeassistant-svc` → `mqtt-svc`
- Clarified Jellyfin ownership model in UID schema

---

## [2025-10-27] Memos Service 📝
### Added
- Memos (self-hosted Notiz-/Journalsystem) mit PostgreSQL-Backend und Traefik-Routing  
  - URL: https://memos.homehill.de  
  - Swarm-Deploy mit Secrets, NFS-Persistenz und Dual-Network (Proxy + DB)  

### Changed
- Best Practice ergänzt: Bei Services mit mehreren Overlays das Label `traefik.docker.network=traefik_traefik_proxy` setzen, um die korrekte Upstream-IP (VIP) für Traefik sicherzustellen  

### Fixed
- 504 Gateway Timeout für Memos im Swarm  
  - App bindet jetzt explizit an `0.0.0.0` via `--addr 0.0.0.0` (statt implizit `localhost`)  
  - Traefik-Network-Disambiguation durch `traefik.docker.network=traefik_traefik_proxy`, wenn mehrere Overlays attached sind  

### Troubleshooting Notes
- Traefik-Dashboard prüfen: HTTP Service `memos@swarm` muss eine Server-IP aus dem Proxy-Overlay anzeigen  
- Aus dem Traefik-Container direkten Request auf die `Server URL` testen (VIP:Port), um Overlay-/Routing-Mesh-Probleme auszuschließen  

---

## [2025.10.07]
### Change
- **hostnames** Project will from now on use FQHN. Old use of hostnames will be  
changed when touched (but will not just be touched to be changed).
- **serviceaccounts** Project will from now on use service accounts (for docker  
and container use only) instead of real person's account (coder, mk3). Service  
accounts will cluster wide use UIDs from 9000 to 9999. 

---

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
- 📋 **Documentation sprint**

---

## Workflow
Changes go to `main` as Conventional Commits; ArgoCD reconciles Orchard from Git,
standalone hosts are applied by hand. Conventions: see `CLAUDE.md`.

---

*Built by Headphonebear 🐻 — with Claude as AI pair engineer since 2026.*
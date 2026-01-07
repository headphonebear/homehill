# Barn 🌾

**Barn** is Bear's primary development desktop (GMKTec K11) running Ubuntu 25.10.
Named after the warm, spacious red barns where you can tinker, blast music, and cozy up in corners.

## Hardware Specs

- **CPU**: AMD Ryzen (with Radeon 780M iGPU, 16GB VRAM allocated)
- **RAM**: 64 GB
- **Storage**:
  - 1 TB NVMe (factory, Windows)
  - 2 TB NVMe (Lexar, Ubuntu installation)
- **GPU**: Radeon 780M (iGPU) + future RTX 3060 (eGPU via Minisforum dock)

## Partition Layout

- `/` (46 GB) – System root
- `/home` (916 GB) – User data, projects, code
- `/srv` (914 GB) – Services, Docker volumes, databases
- `/boot/efi` (1.1 GB) – EFI boot partition

## User Schema

Barn follows the Homehill UID/GID schema (2001-2010):

- `coder` (UID 2003) – Primary development user
- `mk3`, `officer`, `headphonebear`, `sounds`, etc. – Themed accounts for different roles

See `homehill/docs/homehill_uid_schema.md` for full details.

## Docker Services

All services run via Docker Compose in isolated subdirectories under `docker/`.

### Currently Running

- **Portainer** – Container management UI (`http://localhost:9000`)

### Planned Services

- **Gitea** – Self-hosted Git server for GitOps workflows
- **Dozzle** – Real-time Docker log viewer
- **Stirling-PDF** – Self-hosted PDF manipulation toolkit
- **BookStack** – Documentation and wiki for Homelab projects
- **n8n** – Workflow automation engine

## How to Deploy Services

Each service lives in its own subdirectory with a `docker-compose.yml`:

```bash
cd ~/projects/homehill/servers/barn/docker/<service-name>
docker compose up -d
```

## To stop a service:
```bash
docker compose down
```
### Philosophy

Barn is the local experimentation and development hub for Homehill:

- **JetBrains IDEs** PyCharm, GoLand, WebStorm, DataGrip, DataSpell, RustRover for serious coding

- **Docker-based services** for local testing before deploying to Orchard (K3s cluster)

- **AI experimentation playground** - Ollama, Stable Diffusion using 780M iGPU (and later RTX 3060 eGPU)

Barn bridges the gap between personal workflow (coding, learning, experimenting) and production infrastructure (Orchard, Mk3, Dovecote).

Maintainer: Bear 🦊🐻  
Established: January 2026  
Status: Active development 🚀  


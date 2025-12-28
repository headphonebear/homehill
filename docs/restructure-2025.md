# Repository Restructure 2025

## Overview

This document explains the 2025 repository reorganization to better reflect Homehill's evolving architecture.

---

## What Changed?

### Old Structure (Flat)
```
homehill/
├── README.md
├── CHANGELOG.md
├── homehill_uid_schema.md
├── dragonfly/
├── memos/
├── navidrome/
├── ntfy/
├── pihole/
├── portainer/
├── postgres/
├── traefik/
├── vaultwarden/
└── k8s/
```

**Problem:** No clear separation between platforms (Swarm vs K8s vs standalone servers)

---

### New Structure (Organized)
```
homehill/
├── README.md                    # Updated with new structure
├── CHANGELOG.md
├── homehill_uid_schema.md
├── docs/                        # NEW: Documentation hub
│   ├── philosophy.md
│   ├── architecture.md
│   └── restructure-2025.md     # This file!
├── swarm/                       # Docker Swarm configs (legacy)
│   ├── dragonfly/
│   ├── memos/
│   ├── navidrome/
│   ├── ntfy/
│   ├── pihole/
│   ├── portainer/
│   ├── postgres/
│   ├── traefik/
│   └── vaultwarden/
├── clusters/                    # NEW: Orchestration platforms
│   └── orchard/                 # Kubernetes (k8s/ moved here)
│       ├── README.md
│       └── manifests/
├── servers/                     # NEW: Standalone servers
│   ├── mk3/                     # Music server (PN50)
│   │   ├── README.md
│   │   ├── docker-compose.yml
│   │   ├── .env.example
│   │   └── .gitignore
└── shared/                      # NEW: Reusable configs
    ├── traefik-base/
    └── backup-scripts/
```

---

## Why This Structure?

### Clear Platform Separation
- **`swarm/`**: Docker Swarm services (being phased out)
- **`clusters/orchard/`**: Kubernetes manifests
- **`servers/`**: Dedicated single-purpose servers

### Better Scalability
- Easy to add new standalone servers (`servers/mk3/`, `servers/cl1/`, etc.)
- Kubernetes configs isolated in `clusters/orchard/`
- Shared resources in `shared/`

### Documentation-First
- **`docs/`** directory for comprehensive guides
- **Philosophy, architecture, migration docs** all in one place
- Per-server README files for specific instructions

---

## Migration Guide

### For Existing Services

**If you're referencing old paths in scripts/configs:**

| Old Path | New Path |
|----------|----------|
| `/dragonfly/` | `/swarm/dragonfly/` |
| `/k8s/` | `/clusters/orchard/manifests/` |
| `/traefik/` | `/swarm/traefik/` or `/shared/traefik-base/` |

### For New Deployments

**Choose the right location:**

1. **Kubernetes service?** → `clusters/orchard/manifests/`
2. **Docker Swarm (legacy)?** → `swarm/`
3. **Dedicated server?** → `servers/<servername>/`
4. **Reusable config?** → `shared/`

---

## Timeline

### Phase 1: Structure Creation (2025-12-28) ✓
- Create new directories
- Add `servers/mk3/` with full configs
- Write documentation

### Phase 2: Move Legacy Configs (Planned)
- Move old service directories to `swarm/`
- Update README.md with new structure
- Test all service deployments

### Phase 3: Swarm Deprecation (2025 Q2)
- Migrate services to Orchard or standalone servers
- Archive `swarm/` directory
- Update documentation

---

## Questions?

**Why not delete Swarm configs immediately?**
- Services are still running on Swarm nodes
- Migration takes time
- Need stable reference during transition

**Why `servers/` instead of `standalone/`?**
- Shorter, clearer name
- Emphasizes physical/dedicated hardware
- Matches mental model better

**Why not Proxmox/VM approach?**
- We prefer container-native deployments
- Lower overhead
- Easier backups and migrations

---

**Created:** 2025-12-28  
**Author:** Ana 🦊 with Headphonebear 🐻  
**Status:** Active

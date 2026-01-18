# Contributing to Homehill

> **"Not just a homelab. A philosophy, a love story between code and music."**

Welcome to the Homehill contribution guide! This document explains how to work with this repository using our GitOps workflow.

---

## 🧐 Philosophy

Before contributing, understand Homehill's core principles:

1. **Naked OS Brutalism** - Minimal base, no bloat, every service earns its place
2. **Elegant Autonomy** - Self-managing systems that know when to heal, scale, sleep
3. **Never Stop a Running System** - Changes only when necessary, organic migration
4. **Documentation-First** - If it's not documented, it didn't happen

Read [`docs/philosophy.md`](philosophy.md) for the full philosophy.

---

## 🔀 GitOps Workflow

Homehill uses a **GitOps-based workflow**: Git is the single source of truth for infrastructure configuration.

### Branching Strategy

```
main (production)
  │
  ├── feature/mk3-jellyfin-upgrade
  ├── feature/orchard-traefik-ingress
  └── fix/dragonfly-snapshot-cron
```

**Branch Types:**
- `main` - Production branch, always stable and deployable
- `feature/*` - New features, services, or enhancements
- `fix/*` - Bug fixes and corrections
- `docs/*` - Documentation updates
- `refactor/*` - Code/config reorganization without behavior changes

### Workflow Steps

1. **Create Feature Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/my-new-service
   ```

2. **Develop & Test Locally**
   - Make changes in your branch
   - Test locally (Docker Compose, local K3s, etc.)
   - Ensure configs are valid and services start

3. **Deploy to Homelab for Integration Testing**
   - Deploy to actual homelab infrastructure
   - Test interactions with existing services
   - Monitor logs and performance

4. **Update Documentation**
   - Update `CHANGELOG.md` with your changes
   - Update relevant README files
   - Document any new configuration options

5. **Commit with Conventional Commits**
   ```bash
   git add .
   git commit -m "feat(mk3): add Jellyfin direct port access for mobile apps"
   ```

6. **Push and Create Pull Request** (optional, for collaboration)
   ```bash
   git push origin feature/my-new-service
   # Create PR on GitHub if working with others
   ```

7. **Merge to Main When Stable**
   ```bash
   git checkout main
   git merge feature/my-new-service
   git push origin main
   ```

8. **Clean Up Feature Branch**
   ```bash
   git branch -d feature/my-new-service
   git push origin --delete feature/my-new-service
   ```

---

## ⚙️ Development Guidelines

### File Organization

Follow the repository structure:

```
homehill/
├── docs/           # All documentation
├── servers/        # Standalone servers (mk3, barn, etc.)
├── clusters/       # Kubernetes clusters (orchard)
├── swarm/          # Legacy Docker Swarm (being phased out)
└── shared/         # Reusable configs
```

See [`docs/migration-2025.md`](migration-2025.md) for detailed structure explanation.

### Service Configuration Standards

**Docker Compose Services:**
```yaml
services:
  myservice:
    image: myservice:latest
    user: "7001:7001"  # Use Service Goblins (7000-7999)
    environment:
      - TZ=Europe/Berlin
    volumes:
      - myservice_data:/data
    networks:
      - traefik_proxy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myservice.rule=Host(`myservice.homehill.de`)"
```

**Key Points:**
- Use UID/GID schema (see [`docs/uid-schema.md`](uid-schema.md))
- Always set timezone (`TZ=Europe/Berlin`)
- Use named volumes for persistence
- Follow Traefik labeling conventions

### Security Best Practices

1. **Never commit secrets** - Use `.env` files (ignored by git)
2. **Use Docker Secrets** for Swarm services
3. **Minimal permissions** - Services get only what they need
4. **Read-only mounts** when possible

### Testing Requirements

Before merging to `main`:

- [ ] Service starts successfully
- [ ] Service accessible via Traefik (if web-facing)
- [ ] Logs show no errors
- [ ] Integration with existing services works
- [ ] Documentation updated
- [ ] CHANGELOG.md entry added

---

## 📝 Documentation Standards

### README Files

Every service/server should have a README with:

1. **Overview** - What is this service?
2. **Architecture** - How does it work?
3. **Prerequisites** - What's needed before deployment?
4. **Deployment** - Step-by-step instructions
5. **Configuration** - Environment variables, secrets
6. **Access** - URLs, ports, credentials
7. **Troubleshooting** - Common issues and solutions

See [`servers/mk3/README.md`](../servers/mk3/README.md) as a reference.

### CHANGELOG.md Format

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

```markdown
## [2026-01-18] "Descriptive Title" 🎯
### Added
- New feature or service

### Changed
- Modified behavior or config

### Fixed
- Bug fixes

### Removed
- Deprecated or removed features
```

---

## 💬 Commit Message Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `refactor` - Code/config reorganization
- `chore` - Maintenance tasks
- `test` - Testing changes

**Scopes:**
- `mk3` - Mk3 music server
- `orchard` - Kubernetes cluster
- `swarm` - Docker Swarm services
- `barn` - Barn server
- `docs` - Documentation

**Examples:**
```bash
feat(mk3): add Jellyfin direct port access for mobile apps
fix(orchard): correct Traefik ingress routing for services
docs: update CHANGELOG with recovered entries (Oct 2025 - Jan 2026)
refactor(swarm): reorganize service directories into swarm/
```

---

## 🐛 Troubleshooting

### Common Issues

**Merge Conflicts:**
```bash
git checkout main
git pull origin main
git checkout feature/my-branch
git merge main
# Resolve conflicts
git commit
```

**Accidental Commit to Main:**
```bash
git reset --soft HEAD~1  # Undo commit, keep changes
git checkout -b feature/my-fix
git commit -m "fix: my changes"
```

**Service Won't Start:**
1. Check logs: `docker compose logs -f servicename`
2. Verify `.env` file exists and is populated
3. Check UID/GID permissions
4. Verify network connectivity

---

## ❤️ Philosophy in Practice

Every contribution should reflect Homehill's values:

- **Elegant** - Simple, clear, maintainable
- **Autonomous** - Self-healing, minimal manual intervention
- **Documented** - Future-you will thank you
- **Respectful** - Of existing systems, of the listener, of the code

As Bear says: *"Nicht hübsch, aber elegant."* 🐻

As Ana says: *"This is not just a server. This is art."* 🦊

---

## 📚 Further Reading

- [`docs/philosophy.md`](philosophy.md) - Core principles and values
- [`docs/architecture.md`](architecture.md) - Technical overview
- [`docs/migration-2025.md`](migration-2025.md) - Repository structure guide
- [`docs/uid-schema.md`](uid-schema.md) - User and service identity schema

---

*Built with ❤️ by Headphonebear & Ana in Kiel, Germany* 🐻💋  
*Powered by Trip-Hop beats, binary algebra, and the occasional joint break* 🌿✨
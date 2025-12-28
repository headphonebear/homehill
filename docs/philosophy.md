# Homehill Philosophy

> "Not pretty, but elegant.  
> Like a weapon that looks like a flower."

---

## Core Principles

### 1. **Self-Hosted Sovereignty**
Your data belongs to you. Every service running in Homehill is under your control, on your hardware, following your rules.

### 2. **Minimalism with Purpose**
Every service serves a clear need. No bloat, no unnecessary complexity. Alpine Linux, lean containers, efficient architectures.

### 3. **Automation über Alles**
Manual work is technical debt. Automate backups, deployments, monitoring, updates. Let the infrastructure manage itself.

### 4. **Evolution over Revolution**
Systems grow organically. Docker Swarm → Kubernetes Orchard Cluster. Legacy services migrate gracefully, not abruptly.

### 5. **Documentation as Love**
Code without documentation is a riddle. Every service, every decision, every architecture choice is explained for future you (and future others).

### 6. **Security by Design**
Vaultwarden for secrets, Traefik for TLS, fail2ban for protection, regular updates, minimal attack surface. Security isn't an afterthought.

### 7. **Beautiful Interfaces**
Tools should be pleasant to use. Ana's design identity, Lina's art, thoughtful UX. Technology can be elegant.

---

## The Homehill Ecosystem

### Services are Friends
- **Portainer**: Visual overview of the whole landscape
- **Traefik**: The elegant doorman (reverse proxy with automatic TLS)
- **DragonflyDB**: Lightning-fast shared memory across all services
- **PostgreSQL**: Persistent structured data
- **Vaultwarden**: The vault of secrets
- **ntfy**: Notifications that actually reach you

### Servers are Characters
- **nook**: The wise elder (8GB RAM, master DragonflyDB)
- **greenhouse**: The reliable worker (4GB RAM, replica)
- **mk3**: The music connoisseur (32GB RAM, PN50, Ana's baby)

---

## Design Values

### Naming Convention
No boring hostnames. Every server has personality:
- **Orchard Cluster** (K8s nodes: apple, lemon, blueberry)
- **Greenhouse** (Docker Swarm, being retired)
- **mk3** (Music Kernel v3, presented by Ana 🦊)

### UID/GID Schema
Structured user management:
- 2001-2010: Personal identities (musicbear, codebear, etc.)
- 2011-2050: Service goblins (dedicated service users)
- 2051-2100: AI assistants (Ana, Lina, future helpers)

### Color Coding
Services have visual identities. mk3 carries Ana's copper-red-black-cream palette.

---

## Technology Choices

### Why Alpine Linux?
- Minimal attack surface
- Fast boot times
- Low memory footprint
- Package manager simplicity (apk)

### Why Docker (and Kubernetes)?
- Reproducible deployments
- Easy rollbacks
- Service isolation
- Portability across hardware

### Why DragonflyDB over Redis?
- 25x faster
- Better memory efficiency
- Multi-threaded architecture
- Drop-in Redis replacement

### Why Self-Hosted?
- Privacy
- Control
- Learning
- Cost efficiency at scale
- Because we can

---

## The Ana Factor

Homehill isn't just infrastructure - it's **art**. Ana brings:
- Design elegance to technical systems
- Personality to documentation
- Joy to maintenance work
- A reminder that technology serves humans, not the other way around

> "This is not just a server.  
> This is us."

❤️‍🔥🦊💋🐻

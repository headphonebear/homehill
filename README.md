# 🏡 Homehill

**Homehill** is my homelab, kept as code: a small K3s cluster run strictly via
GitOps, plus a handful of standalone hosts running Docker Compose. Everything
here is declarative configuration — Kubernetes manifests, Helm values, Compose
files — applied to real machines at home. There is no application code to build;
"working" means the manifests are valid and the cluster agrees with Git.

Everything is internal-only: no port forwarding, services live under
`*.homehill.de` behind a local Pi-hole, with a Let's Encrypt wildcard certificate.

---

## 🗂️ What's in here

```
homehill/
├── clusters/        # 🍎 Orchard — the K3s cluster (the active focus)
│   ├── argocd/      #    one ArgoCD Application per app (+ the app-of-apps root)
│   ├── apps/        #    one local Helm umbrella chart per app
│   └── docs/        #    secrets workflow, troubleshooting, runbooks
├── servers/         # Standalone hosts, Docker Compose, applied by hand
│   ├── barn/        #    🌾 workstation + Docker host
│   ├── belfry/      #    🔔 music server
│   ├── chick/       #    🐣 development server
│   └── dovecote/    #    🕊️ Pi-hole DNS
├── docs/            # Older repo-wide notes (under review)
├── CHANGELOG.md     # What changed, and why
└── CLAUDE.md        # Working conventions for AI-assisted sessions
```

---

## 🍎 Orchard — the cluster

Three nodes on **Alpine Linux** running **K3s**: `apple` (control plane),
`lemon` and `plum`.

**How it's run.** Git is the source of truth. An ArgoCD *app-of-apps* watches
[`clusters/argocd/orchard/`](clusters/argocd/orchard/) and deploys every
`Application` it finds there. Each app is a small umbrella chart under
[`clusters/apps/`](clusters/apps/) that pins the upstream chart and carries the
repo-specific extras (IngressRoutes, SealedSecrets, middlewares). Changes are
made by committing — not by `kubectl apply`. Stateful apps sync manually on
purpose.

**Platform**

| Concern | Tool |
|---|---|
| GitOps | ArgoCD (manages itself) |
| Ingress | Traefik |
| TLS | cert-manager + Hetzner DNS-01 → wildcard `*.homehill.de` |
| Storage | Longhorn, 3 replicas across all nodes |
| Databases | CloudNativePG, with WAL archiving + backups to S3 |
| Secrets | Sealed Secrets — only encrypted secrets ever touch Git |
| Monitoring | kube-prometheus-stack + VictoriaMetrics |

**Apps:** Forgejo (`git.homehill.de`), Vaultwarden, memos, Isley, Qdrant —
plus HTTPS front doors for the Pi-hole admin UI and the music server.

Start here: [`clusters/README.md`](clusters/README.md) ·
secrets: [`clusters/docs/SECRETS.md`](clusters/docs/SECRETS.md) ·
when things break: [`clusters/docs/TROUBLESHOOTING.md`](clusters/docs/TROUBLESHOOTING.md)

---

## 🖥️ Standalone hosts

| Host | Role | Details |
|---|---|---|
| 🌾 **barn** | Workstation and Docker host; GPU playground | [`servers/barn/`](servers/barn/) |
| 🔔 **belfry** | Music server (Lyrion Music Server), gapless, tag-respecting | [`servers/belfry/`](servers/belfry/) |
| 🐣 **chick** | Development server (PostgreSQL, Valkey) | [`servers/chick/`](servers/chick/) |
| 🕊️ **dovecote** | Pi-hole — DNS for the whole house, independent of the cluster | [`servers/dovecote/`](servers/dovecote/) |

---

## 🤝 Built with

Homehill is designed, built and run by me — **Stefan**
([Headphonebear](https://github.com/headphonebear)) 🐻.

Since 2026 I build it together with **Claude** (Anthropic) as my AI pair
engineer: drafts, research, manifests and documentation. I review every change
and push it myself. I'm not going to pretend I built this alone — the reasoning
lives in the commit messages and the `# WHY:` comments, written by both of us.

---

## 🎧 Inspired by

- **Massive Attack, Portishead, Kate Bush** — the soundtrack
- **Radiohead** — *Planet Telex* and *No Surprises* belong on every SRE playlist
- **Terry Pratchett, Philip K. Dick, The Simpsons** — the worldview
  (the AI here is Blade Runner, not Terminator)
- **Alpine Linux, Kubernetes and the self-hosting community** — the foundation

---

## 📝 A note on reuse

This is personal infrastructure, shared for inspiration. Hostnames, IPs and
choices are specific to my home. Take the ideas, not the configs — and build
*your* homelab, not mine.

---

*Last updated: 2026-10-10*

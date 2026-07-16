# Dovecote 🕊️

**Dovecote** is a Dell Wyse 3040 thin client — the tiny, silent, low-power box
that serves DNS + ad-blocking (Pi-hole) for the whole homehill network.

Named for the little house where doves roost: small, quiet, always home.

## Hardware

- **CPU**: Intel Atom x5-Z8350 @ 1.44 GHz (4 cores)
- **RAM**: 2 GB
- **Storage**: 8 GB eMMC (soldered — `/` is a ~5 GB partition, ~4 GB free)
- **OS**: Alpine Linux 3.22, kernel 6.12-lts
- **Address**: `192.168.1.101` (steady) — `dovecote` on the LAN

## History

Until 2026-07-16, Dovecote was one of three managers in a **legacy Docker
Swarm** (alongside the now-freed N150s `greenhouse` + `nook`). That Swarm was
dissolved; every stack on it was dead/unused **except Pi-hole**, which is the
one thing this box now exists for. Docker was wiped clean (`/var/lib/docker`)
and the OS left in place — no reinstall needed (it was already lean).

## What runs here

- **[pihole/](pihole/)** — Pi-hole v6 in Docker (host networking), the network's
  DNS + ad-blocker. HTTPS admin UI is fronted by Orchard's Traefik at
  `https://pihole.homehill.de/admin` (see `clusters/apps/pihole/`).

## Deploy model

Applied **manually** on the host (this box does not Git-pull — yet). The repo
is the source of truth; to deploy, copy the compose to `~/pihole/` on Dovecote
and `docker compose up -d`. See `pihole/README.md`.

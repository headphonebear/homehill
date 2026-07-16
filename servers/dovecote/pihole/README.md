# Pi-hole on Dovecote 🕳️

Network-wide DNS + ad-blocking for homehill. This is the **production** Pi-hole
(migrated here 2026-07-16 after the Swarm teardown). Runs as a single Docker
container with **host networking** — Dovecote has port 53 free and no local
resolver, so no port-mapping gymnastics needed.

## Access

- **DNS**: `192.168.1.101:53` — the router (TP-Link AX3000) hands this out as the
  network DNS server via DHCP.
- **Admin UI**: `https://pihole.homehill.de/admin`
  (valid `*.homehill.de` cert, reverse-proxied by Orchard's Traefik — see below).
  Directly: `http://192.168.1.101/admin`.

## HTTPS is done in the cluster, not here

The pretty HTTPS front door lives in **`clusters/apps/pihole/`** (GitOps): Orchard's
Traefik terminates TLS with the wildcard cert and reverse-proxies to this box via
a `type: ExternalName` service → `192.168.1.101:80`. **DNS itself stays fully
independent of the cluster** — only the admin URL is coupled. Cluster down? DNS
keeps working; reach the UI directly on the IP.

## Deploy

Manual (this host does not Git-pull). From this repo:

```bash
scp docker-compose.yaml dovecote:~/pihole/docker-compose.yaml
ssh dovecote 'cd ~/pihole && docker compose up -d'
```

Data (gravity.db, pihole.toml, TLS certs, gravity lists) lives in `./etc-pihole/`
**on Dovecote** — gitignored here, never committed (it holds the admin password
hash and certs).

## Gotchas worth knowing

- **Image is digest-pinned**, not `:latest` — bump deliberately (see the compose
  header comment for the current tag/version).
- **No `FTLCONF_webserver_api_password` env** on purpose: an enforced env var
  overrides any UI-set password on every restart. Set the password IN Pi-hole
  (`Settings` or `pihole setpassword`); it persists in `pihole.toml`.
- **`FTLCONF_dns_listeningMode=all`** is set so LAN clients always get answers.
- **Config backup**: use Pi-hole's Teleporter (Settings → Teleporter) for a full
  export — that's how this instance was seeded.

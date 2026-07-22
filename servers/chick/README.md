# Chick 🐣

**Chick** is the homehill **development server** — a small, fast, well-fed
scratchpad for building things (databases, a Python dev environment) before
they graduate to a real home.

Named for a hatchling: freshly out of the egg, room to grow.

## Hardware

- **CPU**: Intel N150 (4 cores) — one of the two N150s freed when the legacy
  Docker Swarm was dissolved (2026-07-16)
- **RAM**: 15.3 GB (+ 4 GB swap)
- **Storage**: one NVMe, ~440 GB free on `/` (single root partition, no separate
  `/srv`)
- **OS**: Alpine Linux 3.23, kernel 6.18-lts
- **Address**: `192.168.1.73` — `chick.homehill.de` on the LAN

## Access

- **User**: `coder` (UID/GID **2003/2003**, matching barn), **key-only** login
  with barn's `coder.pub`, member of the `docker` group (rootless containers).
  ```bash
  ssh -i ~/.ssh/coder -o IdentitiesOnly=yes coder@192.168.1.73
  ```
- **root**: was provisioned with a throwaway password for bring-up — retire it
  once everything runs as `coder`.

## What runs here

- **Docker** (29.5.2 + compose v2.40.3), enabled at boot. Installed from Alpine's
  `community` repo (which had to be un-commented in `/etc/apk/repositories`).
- Stacks live under `servers/chick/<service>/` — **none yet**, they're coming.

## The plan

Goal: the coolest dev server this hardware allows, driven from PyCharm on barn.

- **Way A — SSH remote interpreter**: PyCharm stays local on barn; chick is the
  database + runtime workhorse. (Deliberately *not* JetBrains Gateway / Remote
  Dev — that would run the whole IDE backend on the N150 and eat its RAM.)
- **Target stack** (Docker, one compose per service): **PostgreSQL +
  DragonflyDB + Qdrant**. Elasticsearch is *out*.
- **Open question**: whether the PyCharm interpreter itself lives natively
  (Alpine musl) or in a container (glibc) — decided when we wire up PyCharm.

## Deploy model

Applied **manually** on the host (this box does not Git-pull). The repo is the
source of truth: to deploy a stack, copy its compose to chick and
`docker compose up -d`. GitOps convention as everywhere else in `servers/`.

## Gotcha — Alpine `adduser -D` locks the account

`adduser -D` creates a passwordless user but writes `!` into the `/etc/shadow`
password field. sshd reads `!` as **"account is locked"** and then refuses *even
key-based* login (log: `User coder not allowed because account is locked`). Fix
without setting a real password — replace `!` with `*` (key-only, but unlocked):

```bash
sed -i 's|^coder:!:|coder:*:|' /etc/shadow
```

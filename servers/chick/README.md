# Chick 🐣

**Chick** is the homehill **development server** — a small, fast, well-fed
scratchpad for building things (databases, a Python dev environment) before
they graduate to a real home. Today its main job is the **database backend of
the [mk3 toolkit](https://github.com/headphonebear/mk3)** (a music collection
treated as data).

Named for a hatchling: freshly out of the egg, room to grow.

## Hardware

- **Box**: ASUS NUC 14 Essential (`NUC14MNK`) — one of the two N150s freed when
  the legacy Docker Swarm was dissolved (2026-07-16)
- **CPU**: Intel N150 (4 cores / 4 threads)
- **RAM**: 15.3 GB (+ 4 GB swap)
- **Storage**:
  - 500 GB NVMe — single root partition (~460 GB on `/`, no separate `/srv`);
    Docker's named volumes live here
  - 1 TB USB HDD at **`/mnt/music`** — a **working copy of the music library
    from belfry** (the music server), read by the mk3 indexer. Copied once with
    rsync (2026-08-09); nothing keeps it in sync automatically. Mounted via
    `fstab` with `nofail`, so chick still boots if the disk is unplugged.
- **OS**: Alpine Linux 3.23, kernel 6.18-lts, OpenRC
- **Address**: `192.168.1.73` — `chick.homehill.de` on the LAN

## Access

- **SSH is key-only.** No root login, no password or keyboard-interactive
  auth. The hardening lives in its own drop-in,
  `/etc/ssh/sshd_config.d/10-homehill.conf`, so openssh upgrades never collide
  with it. (`Include` sits at the top of `sshd_config` and sshd takes the first
  value it sees, so the drop-in wins over the stock `PermitRootLogin yes`.)
- **User**: `coder` (UID/GID **2003/2003**, matching barn), key-only login with
  barn's `coder.pub`.
  ```bash
  ssh -i ~/.ssh/coder -o IdentitiesOnly=yes coder@192.168.1.73
  ```
- **Root** is reached from a `coder` session — `doas` for `coder`
  (`/etc/doas.d/coder.conf`), or `su -`. There is no `sudo` on this box.
- `coder` is in the `docker` group. Mind that this is **root-equivalent** (anyone
  who can start containers can mount the host filesystem), not "rootless".

## What runs here

- **Docker** (29.5.2 + compose v2.40.3), enabled at boot. Installed from Alpine's
  `community` repo (which had to be un-commented in `/etc/apk/repositories`).
- **Stacks** — one compose per service under `servers/chick/<service>/`:

  | Stack | Image | Role |
  |-------|-------|------|
  | [`postgres/`](postgres/docker-compose.yaml) | `postgres:16-alpine` | mk3's source of truth: albums / tracks / paths, keyed on MusicBrainz IDs |
  | [`valkey/`](valkey/docker-compose.yaml) | `valkey/valkey:8-alpine` | mk3's work-queue + MusicBrainz cache (AOF, `noeviction`) |

  Both bind to **`127.0.0.1` only** — the mk3 code runs on chick itself (Way A,
  below). The bind address is an `.env` knob for the day tools run from barn.
  The *why* behind each choice (Valkey over Dragonfly, `noeviction`, …) is in
  the compose files.
- **mk3 jobs** run as one-shot containers built locally on chick (the indexer
  reads `/mnt/music` read-only and writes to Postgres) — batch jobs, not
  services.

## The plan

Goal: the coolest dev server this hardware allows, driven from PyCharm on barn.

- **Way A — SSH remote interpreter**: PyCharm stays local on barn; chick is the
  database + runtime workhorse. (Deliberately *not* JetBrains Gateway / Remote
  Dev — that would run the whole IDE backend on the N150 and eat its RAM.)
- **Target stack** (Docker, one compose per service): **PostgreSQL + Valkey**
  (live) **+ Qdrant** (later — deliberately not installed until similarity
  search is on the table). Elasticsearch is *out*. Valkey replaced the
  originally planned DragonflyDB: Dragonfly's many-core design is wasted on a
  4-core N150, and all three speak RESP, so the code doesn't care.
- **Open question**: whether the PyCharm interpreter itself lives natively
  (Alpine musl) or in a container (glibc) — decided when we wire up PyCharm.

## Deploy model

Applied **manually** on the host (this box does not Git-pull, and has no `git`
yet). The repo is the source of truth: to deploy a stack, copy its folder to
`~/stacks/` on chick, create `.env` from `.env.example`, then
`docker compose up -d`. GitOps convention as everywhere else in `servers/`.
Real `.env` files never get committed (see [`.gitignore`](.gitignore)).

## Gotcha — Alpine `adduser -D` locks the account

`adduser -D` creates a passwordless user but writes `!` into the `/etc/shadow`
password field. sshd reads `!` as **"account is locked"** and then refuses *even
key-based* login (log: `User coder not allowed because account is locked`). Fix
without setting a real password — replace `!` with `*` (key-only, but unlocked):

```bash
sed -i 's|^coder:!:|coder:*:|' /etc/shadow
```

## Gotcha — `n_live_tup` reads 0 after a restart

After recreating the Postgres container, `pg_stat_user_tables.n_live_tup` showed
**0 rows everywhere**. That is just the statistics being reset, not data loss.
Count for real with `count(*)` before you panic.

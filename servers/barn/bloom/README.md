# bloom 🌸 — SwarmUI on barn

**bloom** is SwarmUI (Stable Diffusion, ComfyUI backend) running on barn's RTX 3060
as a persistent service, reachable in Homehill at `https://bloom.homehill.de`.
Owner/admin: `ai`. Decided 2026-10-17 (Seed → Blüte).

Full write-up in Outline: `Homehill` → "🌸 bloom — SwarmUI (Stable Diffusion) auf barn".

## What lives where

| Piece | Where | In Git |
|-------|-------|--------|
| SwarmUI install (clone, `pybin/`, models, outputs) | `/srv/ai/SwarmUI` | no — upstream clone + data |
| Launcher | `/srv/ai/SwarmUI/start-swarmui.sh` | ✅ `start-swarmui.sh` (this dir) |
| systemd unit | `/etc/systemd/system/bloom.service` | ✅ `bloom.service` (this dir) |
| SwarmUI settings | `/srv/ai/SwarmUI/Data/Settings.fds` | no — see below |
| Users + password hashes | `/srv/ai/SwarmUI/Data/Users.ldb` | **never** |
| HTTPS front door (Traefik, ExternalName) | Orchard | ✅ `clusters/apps/bloom/` (coder) |

## Install / update the service

```bash
sudo install -m 644 bloom.service /etc/systemd/system/bloom.service
install -m 775 start-swarmui.sh /srv/ai/SwarmUI/start-swarmui.sh
sudo systemctl daemon-reload
sudo systemctl enable --now bloom
```

**WHY these unit choices** (details as comments in `bloom.service`):

- `KillSignal=SIGINT` — SIGINT is SwarmUI's orderly shutdown: it saves user data and
  frees VRAM. SIGTERM would skip that.
- `Restart=on-failure`, `RestartSec=15` — the OCuLink eGPU is not always ready at boot.
- `UMask=0002` — `/srv/ai` is shared by the `ai` group (setgid dirs); keep files
  group-writable.
- No GPU juggling in the unit: SwarmUI frees VRAM on its own after 10 idle minutes.
  Stop the service by hand only when the GPU is needed for something else.

## Settings that differ from SwarmUI's defaults

`Settings.fds` is ~500 lines of mostly defaults, and some fields hold values that
don't belong in Git (e.g. OAuth client secret slots). So it is **not** committed.
Instead, these are the deliberate choices — set them via *Server → Server
Configuration*, or in the file followed by a restart:

| Setting | Value | WHY |
|---------|-------|-----|
| `Network.Host` | `0.0.0.0` | Orchard's Traefik reaches barn `:7801` over the LAN (ExternalName). |
| `Network.Port` | `7801` | SwarmUI default; the ExternalName points here. |
| `UserAuthorization.AuthorizationRequired` | `true` | **Login is mandatory in the network.** Without it SwarmUI trusts the `X-SWARM-USER_ID` header — anyone could be anyone. |
| `UserAuthorization.AllowLocalhostBypass` | `true` | Local barn users skip login (as `owner`). Proxy-safe: SwarmUI checks the socket IP *and* the absence of `X-Forwarded-For` (`src/Utils/WebUtil.cs`), so Traefik traffic never counts as local. Trade-off: every local barn account is `owner`. |
| `UserAuthorization.InstanceTitle` | `bloom` | Name on the login page. |
| `UserAuthorization.LoginNotice` | "Willkommen bei bloom 🌸 …" | Tells people where to ask (Bear or the Hive). |
| `Backends.ClearVRAMAfterMinutes` | `10` | Measured 2026-10-17: ~6.9 GB after an SDXL image → ~230 MiB after 10 idle minutes. This is what makes a 24/7 service OK next to other GPU users. |

⚠️ Set `LoginNotice`/auth settings **via the file + restart**, not via the API: as of
v0.9.8.1 the API's lock-out guard checks the wrong key (`authorization.*` instead of
`userauthorization.*`). Upstream bug, not yet reported.

## Accounts

Created by Stefan in the SwarmUI UI (2026-10-17): `bear` (owner), `bearin`,
`headphonebear`, `misty` (role `user`). Mid-term plan: SSO via Authentik together
with `coder`, then logins move there.

## Version

SwarmUI v0.9.8.1 @ `3bf165e` (master, unpinned), ComfyUI 0.28.0 (AutoUpdate off),
torch 2.13.0+cu130 — as of 2026-10-17.

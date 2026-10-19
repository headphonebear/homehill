# 🪪 Homehill UID/GID Schema

A fixed numbering scheme for user and service identities across all Homehill
hosts (and the Orchard cluster), so that file ownership means the same thing
everywhere — on barn, on chick, on an NFS share, inside a pod.

## Ranges

| Range | Category | What lives here | Examples |
|---|---|---|---|
| `1000–1999` | **System / defaults** | Distro defaults and container-image users | `1000` (common image default) |
| `2000–2999` | **Stefan's accounts** | One account per role — data is owned by the role it belongs to | `mk3`, `coder`, `tinkerbear` |
| `3000–3999` | **Frau Bär's accounts** | Same idea, second person in the household | `tinkerbearin` |
| `7000–7999` | **Service users ("service goblins")** | Long-running services; they *run* things, they don't *own* the data. `7xxx` mirrors the `2xxx` account it serves (`3xxx`: open, see below) | `ai-svc` 7007 |
| `9000–9999` | **Linked AI accounts** | An AI identity tied to a personal account, if one is wanted. `9xxx` mirrors it the same way | `ai` → 9007 (reserved, not created) |

UID and GID are always the same number.

## Personal accounts

| User | UID/GID | Role |
|---|---|---|
| `mk3` | 2001 | 🎵 Music archivist — keeper of the FLAC collection |
| `officer` | 2002 | 🗂️ Office and finances |
| `coder` | 2003 | 💻 Infrastructure and code — homelab, this repo, the dev server |
| `headphonebear` | 2004 | The alter ego on stage — public face, blog, music, writing 🎧 |
| `sounds` | 2005 | 🎛️ Music tinkering, synthesizers |
| `misty` | 2006 | 🕶️ Websurf account — the sandbox for the toxic corners of the web (Tor, proxy, no logged-in browser) |
| `ai` | 2007 | 🔬 AI lab |
| `playbear` | 2008 | 💤 Inactive — exists on barn (since 2026-01), role not written down yet |
| `tinkerbear` | 2009 | 🛠️ Tinkering, 3D printing, indoor gardening 🌿 |
| `stefan` | 2010 | 📷 "The Stefan" — family photos, personal documents |
| `film` | 2011 | 💤 Inactive — exists on barn (since 2026-01), role not written down yet |
| `tinkerbearin` | 3009 | 🎨 Frau Bär — 3D printing and painting |
| `bearin` | 3012 | 🐻 Frau Bär — "everything for now", home of her own Claude (owlhome) |

The two personal ranges mirror each other: `tinkerbear` 2009 ↔ `tinkerbearin`
3009, `bearin` 3012 ↔ `bear` 2012 (decided, not created yet).

`coder` (2003) is the account used on barn, chick and owlhome, and the one
AI-assisted sessions run as.

Accounts live only where they're used: `bearin` exists on owlhome only (not on
barn — decided 2026-10-17, add it when she needs something there).
`tinkerbearin` also exists on barn, for a historical reason unrelated to today's
setup.

## Service users

**The goblin rule (Stefan, written down 2026-10-19):** a service user takes the
number of the account it serves, with a `7` in front instead of the `2`:
`ai` 2007 → `ai-svc` 7007. The `9xxx` range mirrors the same way for linked AI
accounts, if one is wanted (`ai` → 9007, reserved). The idea is older than this
page; it never made it into writing, which is how the first three entries below
came to break it.

⚠️ **Open:** Frau Bär's `3xxx` accounts would land on the same `7xxx` numbers as
Stefan's (`tinkerbear` 2009 and `tinkerbearin` 3009 → both 7009). How her goblins
are numbered is still to be decided.

| User | UID/GID | Service | Status |
|---|---|---|---|
| `memos-svc` | 7001 | 📝 memos (on Orchard; matches file ownership on the NFS media share) | active |
| `mqtt-svc` | 7002 | 🏠 MQTT / Node-RED (home automation) | reserved |
| `jellyfin-svc` | 7003 | 🪦 Jellyfin | retired — replaced by belfry; **don't reuse** the number |
| `ai-svc` | 7007 | 🌻 Ingestor (Outline → Qdrant CronJob on Orchard, image `homehill/ingestor`). First user under the goblin rule | active |

7001–7003 predate the written goblin rule and don't follow it (7001 would be
`mk3`'s goblin). They stay as they are — renumbering would mean re-owning files
on the NFS share for no gain — and their numbers are simply taken.

Retired numbers stay retired: old files with that owner may still be around,
and a new service must never inherit them by accident.

## Principles

**Data owner vs. service runner.** A role account (e.g. `mk3`) owns the data.
A service user (e.g. `memos-svc`) only runs the service and owns nothing but
its own config/state directories. Services get the minimum access they need —
usually read-only mounts.

**Migrate organically.** Existing services move to the scheme when they're
touched anyway (new version, config change), not just for the sake of it. New
services use the scheme from day one.

### Checklist for a new or migrated service

- [ ] Pick the next free `7xxx` number and add it to the table above
- [ ] Create the user/group with UID = GID
- [ ] Check ownership: data stays with its role account, the service gets read-only where possible
- [ ] Set the UID in the Compose file / pod `securityContext`, with a `# WHY:` pointing here
- [ ] Test, then note it in `CHANGELOG.md`

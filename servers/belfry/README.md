# 🔔 belfry — Music Server

> A self-hosted, tag-respecting, gapless music system built on **Lyrion Music
> Server (LMS)**. No cloud, no accounts, nothing fetched from the internet —
> the library is a curated FLAC collection and stays exactly as tagged.

belfry is the **brain**: it holds the library, the play queue, and the control
surface. Sound comes out of separate **players** that connect to it. It replaces
the retired Ana-era stack (Jellyfin + Navidrome), which fought the collection's
curated tags and could not drive the household's hardware gaplessly.

---

## Architecture

```
                 curated FLACs (btrfs, /srv/music, owned by mk3)
                                  │  read-only
                                  ▼
                       ┌──────────────────────┐
                       │   Lyrion Music Server │   the brain: library,
                       │   (belfry-lms)        │   queue, tag-faithful index
                       └───────────┬──────────┘
              SlimProto :3483      │      UPnP Bridge (squeeze2upnp)
        ┌─────────────────────────┼───────────────────────────┐
        ▼ native, bit-perfect     ▼                            ▼ DLNA/UPnP
  squeezelite endpoints     (control)                    fixed appliances
  e.g. hummingbird          Material Skin           Küche · Denon DRA-800H
  (Pi3 + HifiBerry          web UI / phone          · [TV] Samsung
   DAC2 HD)                 :9000/material/         (can't install software)
```

- **Native players (best quality):** `squeezelite` on a Pi with a HifiBerry DAC
  → bit-perfect FLAC, gapless, queue held server-side. `hummingbird` = Pi 3B +
  HifiBerry **DAC2 HD**. (Endpoints carry bird names; the Denon streamer is
  `nightingale`.)
- **DLNA appliances (can't run our software):** reached via the LMS **UPnP
  Bridge**, which presents each DLNA renderer to LMS as a player. The queue
  stays in LMS, so playback survives the phone/remote leaving the network.
- **Remote:** **Material Skin** (LMS' built-in web UI), works as a phone
  home-screen web app.

### Why the queue lives in the server
A control point that leaves the network must not stop the music. LMS holds the
queue and feeds the next track itself — for native *and* bridged players.

---

## Stack (`docker-compose.yml`)

| Service            | Role                                              |
|--------------------|---------------------------------------------------|
| `belfry-lms`       | Lyrion Music Server (host networking — see below) |
| `belfry-postgres`  | Reserved for the future **mk3 toolkit** (empty)   |
| `belfry-dragonfly` | Reserved cache for the mk3 toolkit                |

> **Postgres + Dragonfly are not used by LMS.** They are provisioned ahead of
> the Python **mk3** toolkit (MusicBrainz enforcement, catalogs, queue jobs).

### Why `network_mode: host` for LMS
The UPnP Bridge discovers DLNA renderers via **SSDP multicast**, which does
**not** traverse Docker's bridge network. On a published-ports bridge setup the
bridge finds **zero** renderers. Host networking is required for the kitchen
speaker / Denon / TV to appear as players.

---

## Host

- **ASUS PN50** (Ryzen 5, 32 GB RAM), Alpine Linux + Docker.
- Music on a 1 TB **btrfs** volume (`/srv/music`, subvolumes `mk3`, `io1`,
  `cl1`, `sg1`), owned by user **`mk3`** (uid/gid 2001) — kept as the historical
  owner of the collection even as the host is renamed to `belfry`.
- Runs from a git checkout of this repo (`~mk3/homehill`); deploy = `git pull`
  + compose.

---

## Setup / Reproduce

The compose is declarative orchestration; a few **one-time, in-app** setup steps
are not captured in git (LMS keeps its state — library DB, plugins, prefs — in
the `belfry-lms-config` volume). To rebuild from scratch:

```bash
# 1. Create the persisted config volume (compose treats it as external)
docker volume create belfry-lms-config

# 2. Bring up the stack (needs servers/belfry/.env — see .env.example)
docker compose -f servers/belfry/docker-compose.yml up -d

# 3. LMS auto-sets its media dir to /music and scans (~10k FLACs takes a while)
```

Then, in the LMS web UI (`http://belfry:9000`):

4. **Install Material Skin** — Settings → Manage Plugins → *Material Skin* →
   apply → restart. (It is the actual modern UI; the default skin is not it.)
5. **Install UPnP Bridge** — Settings → Manage Plugins → *UPnP Bridge*
   (philippe44) → apply → restart. Requires host networking (see above).
6. **Disable all internet lookups** (enforces the "nothing from the net" policy):
   - `server.prefs`: `noContributorPictures: 1`
   - `plugin/musicartistinfo.prefs`: set `lookupArtistPictures`,
     `browseArtistPictures`, `lookupAlbumArtistPicturesOnly`, `lookupCoverArt`,
     `useAIGeneratedContent`, `runImporter` all to `0`.

Access: **`http://belfry:9000/material/`**.

---

## Collection policy

- Only **MusicBrainz-conformant** tagged material enters the library.
- The **Genre** field is intentionally left empty.
- **Nothing is fetched from the internet.** Album covers come from the files;
  artist images (Kodi-style `folder.jpg` / `fanart.jpg` per artist) are local —
  wiring LMS to read those local artist images is a planned enhancement.

---

## Status / pending

- [ ] Cut over from the old hand-run container / `servers/mk3` stack to this one.
- [ ] Rename host `mk3.homehill.de` → `belfry.homehill.de` (DNS + hostname +
      LMS server name) — sequenced deliberately.
- [ ] Ingress: valid TLS + nice hostname via the **Orchard cluster Traefik**
      (ExternalName + IngressRoute, same pattern as Pi-hole). Until then, LMS is
      reached directly at `:9000`.
- [ ] Exclude native players from the UPnP Bridge (avoid double-registration of
      a Pi that also advertises DLNA).
- [ ] Denon DRA-800H over DLNA: confirm FLAC vs. force-transcode (advertised
      `protocolInfo` didn't confirm FLAC; hardware does support it).

---

*Built by 🐻 Headphonebear & 🤖 Claude — successor to the mk3 music server.*

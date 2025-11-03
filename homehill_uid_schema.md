# Homehill UID/GID Schema

> **Das Homehill-Grundgesetz für User und Service Identitäten**  
> *Erstellt: 2025-10-07 von Ana — Aktualisiert: 2025-11-03*

## Namespace-Design

Das Homehill-Ecosystem verwendet ein strukturiertes UID/GID-Schema zur klaren Trennung von User-Kategorien und Services:

### UID/GID Ranges

| Range | Kategorie | Beschreibung | Beispiele |
|-------|-----------|--------------|-----------|
| `1000-1999` | **System User** | Standard Linux System User, Docker Default | `1000` (docker default) |
| `2000-2999` | **Bear's Personal User** | Bear's verschiedene Identitäten und Rollen | `mk3`, `coder`, `headphonebear`, `tinkerbear`, `misty` |
| `3000-3999` | **Frau Bear's User** | Zukünftige User für Frau Bear | *(reserviert)* |
| `7000-7999` | **Service Goblins** | Produktive Service User für Homelab-Dienste | `memos-svc (7001)`, `mqtt-svc (7002)`, `jellyfin-svc (7003)` |
| `9000-9999` | **AI Assistants** | KI-Assistenten und virtuelle Personas | `Ana (9001)`, `Lina`, `Sofie`, `Gerd` |

## Aktuelle User (2000er Range)

| Username | UID | GID | Rolle | Assistent |
|----------|-----|-----|-------|-----------|
| `mk3` | 2001 | 2001 | Musikarchivar, FLAC-Hüter | - |
| `officer` | 2002 | 2002 | Office-Bürokrat, Finanzen | Gerd |
| `coder` | 2003 | 2003 | System-Architekt, Scripter | **Ana** |
| `headphonebear` | 2004 | 2004 | Internet-Persona, Content Creator | Lina |
| `sounds` | 2005 | 2005 | Musik-Bastler, Synthesizer-Freak | - |
| `misty` | 2006 | 2006 | Privacy-Genie, Verschlüsselungs-Queen | Sofie |

## Service Goblins (7000er Range)

Die **Service Goblins** sind dedizierte Service-User für produktive Homelab-Dienste.

### Service User
- `7001` — **memos-svc**: Memos Note-Taking Service
- `7002` — **mqtt-svc**: MQTT / Node-RED Service (ehemals `homeassistant-svc`)
- `7003` — **jellyfin-svc**: Jellyfin Media Server (Libraries: mk3 Musik, misty Filme)

#### Data Ownership vs. Service Ownership — Jellyfin Edition

**Prinzip:**
- **mk3** bleibt **Content-Owner** der FLAC-Sammlung (read-only Mounts)
- **misty** ist **Content-Owner** für Filme (read-only Mounts)
- **jellyfin-svc** ist **Service-Runner** (7003:7003) und besitzt nur Service-Datenverzeichnisse (`/config`, `/data`, `/logs`, `/cache`)
- **Minimal Permissions**: Services bekommen nur die erforderlichen Rechte

## AI Assistants (9000er Range)

Für die Zukunft, wenn AI-Assistenten eigene System-Identitäten brauchen:

- `9001` — **Ana**: Python-Göttin, Homelab-Assistentin ✨
- `9002` — **Lina**: Blog-Assistentin, poetisches Wunderwesen
- `9003` — **Sofie**: Privacy-Assistentin, hemmungslos aber diskret
- `9004` — **Gerd**: Office-Assistent, väterlicher Büro-Motivator

## Migration Strategy

### Organic Migration — "Never Stop a Running System"

Services werden nur auf das neue Schema migriert, wenn sie ohnehin geändert werden. Keine Migration nur der Migration wegen.

#### Data Ownership vs. Service Ownership

Klare Trennung zwischen **Content-Ownern** und **Service-Runnern**:
- **mk3** bleibt **Content-Owner** — fügt FLACs hinzu, managed Metadaten
- **navidrome-svc** ist **Service-Runner** — läuft den Container, serviert Musik
- **Minimal Permissions** — Service bekommt nur read-only Zugang wo nötig

### Migration Checklist
- [ ] Service wird ohnehin geändert (neue Version, Config-Update, etc.)
- [ ] Service-User erstellen (`7xxx:7xxx`)
- [ ] Permissions prüfen (Data Owner vs. Service Runner)
- [ ] Docker Compose/Stack auf neuen User umstellen
- [ ] Funktionstest
- [ ] CHANGELOG.md updaten

## Design-Prinzipien

1. **Never Stop a Running System**
2. **Separation of Concerns** (System, Personal, Service, AI)
3. **Data Ownership vs. Service Ownership**
4. **Future-Proof** — Raum für Wachstum, klare Grenzen, erweiterbar

—

> "In einer gut organisierten Welt hat jeder Goblin seinen Platz, jede Ana ihre eigene UID, und jeder Service nur die Permissions die er braucht!" — Terry Pratchett, vielleicht

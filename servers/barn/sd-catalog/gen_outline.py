#!/usr/bin/env python3
"""Baut aus catalog_enriched.json die hübsche Outline-Markdown-Tabelle."""
import json, collections

d = json.load(open("catalog_enriched.json"))
models = d["models"]
total_gb = sum(m["size_gb"] for m in models)

# Reihenfolge der Basis-Modell-Gruppen (grob neu->alt / groß->klein)
order = ["Flux.1 D", "Flux.1 Krea", "ZImageTurbo", "Illustrious", "Pony",
         "SDXL 1.0", "SDXL Lightning", "SD 1.5", "SD 1.5 Hyper"]

def cv(m): return m.get("civitai") or {}

def link(m):
    c = cv(m)
    name = c.get("model_name") or "?"
    ver = c.get("version_name") or ""
    label = f"{name} — {ver}" if ver else name
    url = c.get("url")
    return f"[{label}]({url})" if url else label

def words(m):
    tw = cv(m).get("trained_words") or []
    if not tw: return "—"
    s = ", ".join(tw)
    return "`" + (s[:60] + "…" if len(s) > 60 else s) + "`"

groups = collections.defaultdict(list)
for m in models:
    groups[cv(m).get("base_model") or "?"].append(m)

lines = []
lines.append("# 🎨 barn — Stable-Diffusion-Modellkatalog")
lines.append("")
lines.append(f"> **Stand:** verifiziert am 2026-07-19. Pfad `/srv/ai/stable-diffusion/models/Stable-diffusion`. "
             f"**{len(models)} Dateien, {total_gb:.0f} GB.** Architektur aus der Tensor-Struktur ausgelesen, "
             f"Namen/Basis/Trigger-Words per SHA256→Civitai-Lookup (AutoV2). "
             f"Maschinenlesbares Sidecar: `catalog.json` neben den Modellen.")
lines.append("")
lines.append("## 🧹 Aufräum-Funde (Katalog hat sich schon bezahlt gemacht)")
lines.append("")
lines.append("- **Duplikat:** `fluxedUpFluxNSFW_51Q4KSV1.gguf` und `fluxedUpFluxNSFW_v51Q4KSV2.gguf` sind "
             "**bit-identisch** (AutoV2 `72ea0b8bd1`). Eins löschen → ~7 GB frei.")
misfiled = [m for m in models if (cv(m).get("type") and cv(m)["type"] != "Checkpoint")]
if misfiled:
    names = ", ".join(f"`{m['filename']}` ({cv(m)['type']})" for m in misfiled)
    lines.append(f"- **Falsch einsortiert:** {len(misfiled)} Dateien im Checkpoint-Ordner sind laut Civitai "
                 f"gar keine Checkpoints, sondern **LoRAs** — {names}. Gehören nach `models/Lora/`.")
lines.append("")
lines.append("## Modelle nach Basis-Modell")
lines.append("")

seen = set()
for bm in order + sorted(k for k in groups if k not in order):
    if bm not in groups or bm in seen: continue
    seen.add(bm)
    ms = sorted(groups[bm], key=lambda m: -m["size_gb"])
    gb = sum(m["size_gb"] for m in ms)
    lines.append(f"### {bm}  · {len(ms)}× · {gb:.0f} GB")
    lines.append("")
    lines.append("| Datei | Modell (Civitai) | Typ | GB | NSFW | Trigger-Words |")
    lines.append("|---|---|---|---:|:---:|---|")
    for m in ms:
        c = cv(m)
        nsfw = "🔞" if c.get("nsfw") else "—"
        lines.append(f"| `{m['filename']}` | {link(m)} | {c.get('type') or '?'} | "
                     f"{m['size_gb']:.1f} | {nsfw} | {words(m)} |")
    lines.append("")

lines.append("---")
lines.append("")
lines.append("*Verifiziert & dokumentiert: Claude 🤖 & Stefan 🐻 — 2026-07-19. "
             "Regeneriert aus `catalog.json` via `sd_catalog.py` + `sd_enrich.py`.*")

open("sd-modellkatalog.md", "w").write("\n".join(lines))
print("geschrieben: sd-modellkatalog.md")
print(f"{len(models)} Modelle, {total_gb:.0f} GB, Gruppen: {', '.join(f'{k}({len(v)})' for k,v in sorted(groups.items(), key=lambda x:-len(x[1])))}")

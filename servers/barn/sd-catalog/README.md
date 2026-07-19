# SD-Modellkatalog (barn)

Werkzeug, um die Stable-Diffusion-Modelle auf **barn** zu inventarisieren — verifiziert
aus den Dateien selbst, nicht aus Dateinamen geraten. Löst das „welches Modell war das
nochmal, und wofür?"-Problem.

Modelle liegen unter `/srv/ai/stable-diffusion/models/Stable-diffusion` (A1111-Layout).

## Workflow (drei Schritte)

```bash
cd servers/barn/sd-catalog

# 1) Lokal inventarisieren: Größe, SHA256 (+AutoV2), Architektur aus Tensor-Struktur,
#    eingebettete __metadata__. Verlässt die Maschine NICHT.
sudo python3 sd_catalog.py > catalog.json          # ~4 min (hasht alle Checkpoints)

# 2) Civitai-Anreicherung: Hash -> Modellname, Basis, Typ, Trigger-Words, Link.
#    Nur der Hash geht raus (an civitai.com), Metadaten kommen zurück. Kein Login.
python3 sd_enrich.py                                # schreibt catalog_enriched.json

# 3) Hübsche Outline-Tabelle bauen (nach Basis-Modell gruppiert).
python3 gen_outline.py                              # schreibt sd-modellkatalog.md
```

## Ergebnisse

- **`catalog.json`** — maschinenlesbares Sidecar, wird nach
  `/srv/ai/stable-diffusion/models/Stable-diffusion/catalog.json` kopiert (`root:ai`, `664`).
- **`sd-modellkatalog.md`** — für Outline, Collection `Homehill`.

Neues Modell dazugekommen? Die drei Schritte erneut laufen lassen — Katalog ist wieder aktuell.

## Notizen

- Der `sha256`-Abgleich findet **Duplikate** (bit-identische Dateien unter verschiedenen Namen).
- Der Civitai-`type` deckt **falsch einsortierte LoRAs** im Checkpoint-Ordner auf.
- Civitai-Suchschlüssel ist der **AutoV2**-Hash (erste 10 Hex-Zeichen des SHA256).

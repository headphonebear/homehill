#!/usr/bin/env python3
"""
Baustein 2 — Civitai-Anreicherung.
Liest catalog.json, fragt je Modell den AutoV2-Hash bei Civitai ab,
schreibt die Treffer zurück. Nur Hash raus, Metadaten rein. Kein Login.
Ausgabe: catalog_enriched.json
"""
import json, time, urllib.request, urllib.error, sys

API = "https://civitai.com/api/v1/model-versions/by-hash/{}"
UA = "homehill-barn-sd-catalog/1.0 (personal homelab inventory)"

def lookup(h):
    req = urllib.request.Request(API.format(h), headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)[:60]

def slim(v):
    """Nur die brauchbaren Felder aus der Civitai-Antwort ziehen."""
    model = v.get("model", {}) or {}
    return {
        "model_name": model.get("name"),
        "version_name": v.get("name"),
        "type": model.get("type"),          # Checkpoint / LORA / ...
        "nsfw": model.get("nsfw"),
        "base_model": v.get("baseModel"),    # SD 1.5 / SDXL / Pony / Illustrious / Flux.1 D ...
        "trained_words": v.get("trainedWords") or [],
        "model_id": v.get("modelId"),
        "version_id": v.get("id"),
        "url": f"https://civitai.com/models/{v.get('modelId')}?modelVersionId={v.get('id')}" if v.get("modelId") else None,
    }

def main():
    d = json.load(open("catalog.json"))
    hits = 0
    for i, m in enumerate(d["models"], 1):
        h = m["autov2"]
        sys.stderr.write(f"[{i}/{d['count']}] {m['filename'][:40]:<40} ")
        sys.stderr.flush()
        data, err = lookup(h)
        if data:
            m["civitai"] = slim(data)
            hits += 1
            sys.stderr.write(f"✓ {m['civitai']['model_name']} [{m['civitai']['base_model']}]\n")
        else:
            m["civitai"] = {"error": err}
            sys.stderr.write(f"✗ {err}\n")
        time.sleep(0.6)
    d["civitai_hits"] = hits
    json.dump(d, open("catalog_enriched.json", "w"), indent=2, ensure_ascii=False)
    sys.stderr.write(f"\nFertig: {hits}/{d['count']} auf Civitai gefunden.\n")

if __name__ == "__main__":
    main()

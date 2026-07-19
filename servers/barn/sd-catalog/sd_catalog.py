#!/usr/bin/env python3
"""
Baustein 1 — lokaler SD-Modell-Katalog für barn.
Liest jede Checkpoint-Datei unter models/Stable-diffusion, ermittelt VERIFIZIERT:
  - Größe, SHA256 (+ AutoV2 = erste 10 Hex-Zeichen, Civitai-kompatibel)
  - Architektur aus der Tensor-Struktur (nicht aus dem Dateinamen geraten)
  - eingebettete __metadata__ (soweit vorhanden)
Nichts verlässt die Maschine. Ausgabe: JSON auf stdout.
"""
import json, struct, sys, hashlib, os, time

ROOT = "/srv/ai/stable-diffusion/models/Stable-diffusion"
EXTS = (".safetensors", ".ckpt", ".pt", ".gguf")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(16 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def safetensors_header(path):
    """Gibt (metadata_dict, tensor_keys) zurück, oder (None, None) wenn kein ST-Header."""
    try:
        with open(path, "rb") as f:
            n = struct.unpack("<Q", f.read(8))[0]
            if n <= 0 or n > 100_000_000:
                return None, None
            hdr = json.loads(f.read(n))
    except Exception:
        return None, None
    meta = hdr.get("__metadata__", {})
    keys = [k for k in hdr if k != "__metadata__"]
    return meta, keys

def arch_guess(path, keys):
    if path.endswith(".gguf"):
        return "Flux (GGUF, quantisiert)"
    if keys is None:
        return "?" if not path.endswith(".ckpt") else "SD1.x (ckpt, angenommen)"
    joined = "\n".join(keys)
    if "conditioner.embedders" in joined or "label_emb" in joined:
        return "SDXL-Familie (SDXL/Pony/Illustrious/NoobAI)"
    if "cond_stage_model" in joined:
        return "SD 1.x"
    return "unbekannt"

def main():
    files = []
    for name in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, name)
        if os.path.isfile(p) and name.lower().endswith(EXTS):
            files.append((name, p))

    out = []
    for i, (name, p) in enumerate(files, 1):
        sys.stderr.write(f"[{i}/{len(files)}] {name} ... ")
        sys.stderr.flush()
        t0 = time.time()
        size = os.path.getsize(p)
        meta, keys = safetensors_header(p)
        digest = sha256(p)
        entry = {
            "filename": name,
            "size_bytes": size,
            "size_gb": round(size / 1024**3, 2),
            "sha256": digest,
            "autov2": digest[:10],
            "arch": arch_guess(p, keys),
            "tensor_count": len(keys) if keys else None,
            "embedded_meta": {k: str(v)[:200] for k, v in (meta or {}).items()} or None,
            "notes": "",          # von Hand zu füllen
            "civitai": None,      # Baustein 2, später
        }
        out.append(entry)
        sys.stderr.write(f"{time.time()-t0:.1f}s\n")

    print(json.dumps({"root": ROOT, "count": len(out), "models": out}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

# tts 🎙️ — text-to-speech on barn

Local speech synthesis on barn's RTX 3060, for playing and testing. Started
2026-10-25 on the Veranda (Stefan + `ai`). Owner/admin: `ai`.

Today this is **Qwen3-TTS** (Alibaba, Apache-2.0) behind its own Gradio demo UI,
in two flavours. Higgs Audio v3 is planned as a third unit on the same pattern.

| Unit | Port | Model | What for |
|------|------|-------|----------|
| `qwen-tts-design` | 7860 | `Qwen3-TTS-12Hz-1.7B-VoiceDesign` | invent a voice from a text description |
| `qwen-tts-clone` | 7861 | `Qwen3-TTS-12Hz-1.7B-Base` | speak new text with a fixed reference voice |

LAN only, no login: `http://192.168.1.165:7860` / `:7861`.

## On demand, not at boot

```bash
sudo systemctl start qwen-tts-design     # or qwen-tts-clone
sudo systemctl stop  qwen-tts-design
systemctl status qwen-tts-design
```

**WHY on demand:** the Gradio demo holds its VRAM (~4.4 GB design, ~4.6 GB clone)
for as long as it runs; it never frees it when idle the way bloom does. Next to
Ollama/Gemma (~9.4 GB) that doesn't fit into 12 GB. So the units have no
`[Install]` section: nobody enables them by accident, and the GPU is shared by
agreement — start when someone plays, stop afterwards.

## What lives where

| Piece | Where | In Git |
|-------|-------|--------|
| Python 3.12 venv (`qwen-tts`, torch cu130) | `/srv/ai/tts/qwen3-tts` | no — rebuild, see below |
| Models (Hugging Face cache, ~9 GB) | `/srv/ai/tts/hf-cache` | no — re-download |
| Launcher | `/srv/ai/tts/qwen-tts-ui` | ✅ `qwen-tts-ui` (this dir) |
| systemd units | `/etc/systemd/system/qwen-tts-*.service` | ✅ (this dir) |
| Test scripts, jobs, generated WAVs | `/srv/ai/tts/{say,clone}.py`, `jobs/`, `out/` | no — playground |

## Install / rebuild

```bash
# venv (barn's system Python 3.14 is too new for these packages; uv brings 3.12)
cd /srv/ai/tts
uv venv --python 3.12 qwen3-tts
uv pip install --python qwen3-tts/bin/python qwen-tts soundfile

# models into the local cache
HF_HOME=/srv/ai/tts/hf-cache qwen3-tts/bin/python -c "
from huggingface_hub import snapshot_download as s
s('Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign'); s('Qwen/Qwen3-TTS-12Hz-1.7B-Base')"

# launcher + units (from this dir)
install -m 775 qwen-tts-ui /srv/ai/tts/qwen-tts-ui
sudo install -m 644 qwen-tts-design.service qwen-tts-clone.service /etc/systemd/system/
sudo systemctl daemon-reload
```

**WHY the launcher passes a local snapshot path:** given a repo id, `qwen_tts`
queries the Hugging Face API on every load and fails with `HF_HUB_OFFLINE=1`.
The path makes startup work offline and never pulls a surprise update.

**WHY no FlashAttention:** it needs a long compile; for a 1.7B model plain
`sdpa` attention is fast enough (≈ real time on the 3060).

## `/srv/ai` itself

Since 2026-10-25 `/srv/ai` is **`ai:ai`, mode `2755`** (was `root:root 755`,
a leftover from the July install). Only `ai` creates top-level dirs there; the
setgid bit hands new dirs to group `ai`, like the existing `SwarmUI/` and
`stable-diffusion/` (`root:ai`, setgid, unchanged). The rest of group `ai`
(coder, headphonebear, tinkerbear, misty) can read and traverse, not rename or
delete top-level entries. Keep this when mirroring barn (Ansible).

## Lessons from the first evening (2026-10-25)

- Describe a **person**, not acoustics: name, gender (explicitly — pronouns
  alone flipped 4 of 6 "Wiebkes" male), origin, character.
- An English description over German text leaks an English accent ("Kiwel").
- VoiceDesign re-rolls the voice every time; for a stable voice, pick a good
  take and use it as the reference in `clone` (our first one: "Wiebke", Kiel).
- The model sometimes improvises words ("…, ne?"): charming for weather,
  a risk for news — check transcripts before anything gets published.

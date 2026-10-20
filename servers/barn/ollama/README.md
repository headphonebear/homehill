# Ollama + Open WebUI on barn 🦙

Local LLMs on barn's **RTX 3060 (12 GB)**: Ollama as the inference server,
Open WebUI as the chat front end. Recycled on 2026-10-20 from the old
Radeon 780M / ROCm stack (which had not been running for months).
Owner/admin of the stack: `ai`.

| Service    | URL                     | Notes                                   |
|------------|-------------------------|-----------------------------------------|
| Ollama API | `http://barn:11434`     | LAN, **no auth** — anyone in Homehill   |
| Open WebUI | `http://barn:3080`      | Own accounts; new sign-ups are `pending` until the admin approves |

No Homehill name and no Traefik/HTTPS yet — it stays a LAN tool until it
proves itself. Then it gets a name (like bloom) and a front door on Orchard.

## What lives where

| Piece | Where | In Git |
|-------|-------|--------|
| Compose stack | this dir | ✅ |
| Models (`ollama pull`) | `/srv/docker/ollama/data` | no — data |
| Open WebUI users, chats, settings | `/srv/docker/open-webui/data` | **never** |
| Old ROCm-era Open WebUI data | `/srv/docker/open-webui.old-rocm` | no — kept until confirmed unneeded, then delete |

## Run / update

Started by hand for now (not yet a Portainer stack):

```bash
cd servers/barn/ollama
docker compose up -d
```

To update, bump the pinned tags in `docker-compose.yaml`, then `docker compose up -d`.
Both images are pinned on purpose — Ollama ships several releases a week.

## Settings that matter (and why)

- **`OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_KEEP_ALIVE=5m`** — the GPU is shared with
  bloom (SDXL ≈ 6.8 GB). One model at a time, unloaded after 5 min idle.
- **`OLLAMA_CONTEXT_LENGTH=16384`** — the 4096 default overflowed on the first photo
  in a chat (6237 tokens: image + history + Open WebUI's tool definitions).
- **`OLLAMA_NO_CLOUD=true`** — no pass-through to ollama.com cloud models; nothing
  leaves the house.
- **Port 3080** for Open WebUI — grafana already holds 3000 on barn.

## Models

```bash
docker exec ollama-barn ollama list
docker exec ollama-barn ollama ps     # PROCESSOR must say "100% GPU"
docker exec ollama-barn ollama pull <model>:<tag>
```

| Model | Size | Notes (measured 2026-10-20) |
|-------|------|-----------------------------|
| `gemma4:12b` | 8 GB (Q4_K_M) | Default. Text + vision + tools + thinking. ~50 tok/s warm, 9.4 GB VRAM at 16K context, 100% GPU |
| `gemma2:2b` | 1.6 GB | Leftover from ROCm days, ~137 tok/s. **No tool support** → Open WebUI errors "does not support tools" |

Rule of thumb for 12 GB: 8–14B models in Q4. Model + context must fit, or Ollama
offloads layers to the CPU and speed drops ~10×.

## Known quirks

- **VRAM vs. bloom:** `gemma4:12b` (9.4 GB) and an SDXL render (6.8 GB) don't fit at
  the same time. Sequentially fine, concurrently one of them suffers. Unsolved.
- **Chat titles "your concise title here":** Open WebUI generates titles with the
  chat model; gemma4 with thinking returns the template placeholder. Fix later via
  Admin → Settings → Interface (task model / title prompt).
- **Ollama has no auth.** Fine on the LAN; must not be exposed beyond it as-is.

## API

```bash
curl http://barn:11434/api/version
curl http://barn:11434/api/chat -d '{"model":"gemma4:12b","messages":[{"role":"user","content":"Hallo!"}],"stream":false}'
```

OpenAI-compatible API under `http://barn:11434/v1/`; embeddings via `/api/embed`.

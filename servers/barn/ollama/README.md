# Ollama + Open WebUI on Radeon 780M

Local LLM inference using Ollama with ROCm AMD support.

## Services

- **Ollama** (http://localhost:11434) – LLM API server
- **Open WebUI** (http://localhost:3000) – Beautiful chat interface

## Hardware

- **GPU**: AMD Radeon 780M (gfx1003)
- **RAM**: 16 GB
- **Model Storage**: `/srv/docker/ollama/models`

## Quick Start

```bash
cd ~/projects/homehill/servers/barn/docker/ollama
docker compose up -d
```

## Loading Models

Pull a model from Ollama Registry:

```bash
docker exec ollama-barn ollama pull llama3.2:3b
docker exec ollama-barn ollama pull phi3:mini
docker exec ollama-barn ollama pull mistral:7b
```

## List Available Models

```bash
docker exec ollama-barn ollama list
```

## Test Model Directly

```bash
docker exec -it ollama-barn ollama run llama3.2:3b
# Type your question, Ctrl+D to exit
```

## Recommended Models for 780M

| Model | Size | Notes |
|-------|------|-------|
| `llama3.2:3b` | 2 GB | Fast, good quality |
| `phi3:mini` | 2.3 GB | Very efficient |
| `qwen2.5:3b` | 2 GB | Great for German & English |
| `gemma2:2b` | 1.6 GB | Smallest, fastest |
| `mistral:7b` | 4 GB | Bigger but still viable |

## Storage

Models are stored in `./models/` which persists on `/srv/docker/ollama/models`.

Check usage:

```bash
du -sh ./models
```

## API Usage

```bash
# List running models
curl http://localhost:11434/api/tags

# Generate response
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llama3.2:3b","prompt":"What is 2+2?"}'
```

## Performance

- **Inference Speed**: ~2-5 sec per token (depends on model & VRAM)
- **First Load**: ~10-30 sec (model context loading)

## Future

- Faster inference with RTX 3060 eGPU
- Integration with Ana + MCP + Qdrant for intelligent agents

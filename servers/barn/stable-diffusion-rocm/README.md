# Stable Diffusion on Radeon 780M

AI image generation using AUTOMATIC1111 WebUI on AMD Radeon 780M iGPU via ROCm.

## Hardware

- **GPU**: AMD Radeon 780M (gfx1103)
- **RAM**: 16 GB (8 GB allocated to GPU)
- **Performance**: Slow but functional (smaller models, 512x512 preferred)

## How to Use

```bash
cd ~/projects/homehill/servers/barn/docker/stable-diffusion-rocm
docker compose up -d

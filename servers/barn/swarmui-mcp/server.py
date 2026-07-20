#!/usr/bin/env -S uv run --python 3.12 --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "mcp>=1.2",
#     "httpx>=0.27",
# ]
# ///
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  swarmui-mcp — a bridge from Claude Code to a locally running SwarmUI      ║
# ╠══════════════════════════════════════════════════════════════════════════╣
# ║  WHY this exists:                                                          ║
# ║    SwarmUI (on barn, /srv/ai/SwarmUI) exposes its ENTIRE feature set as a  ║
# ║    plain JSON-over-HTTP API on localhost:7801 — the web UI is just one     ║
# ║    client of it. This little MCP server makes that same API reachable as   ║
# ║    *tools* Claude can call mid-conversation. Thin bridge, full reach.      ║
# ║                                                                            ║
# ║  WHY on-demand only:                                                       ║
# ║    SwarmUI is started by hand (`swarmui`) and Ctrl+C frees the RTX 3060's  ║
# ║    VRAM. This bridge does NOT auto-start it — if SwarmUI is down, the      ║
# ║    tools say so politely. On-demand philosophy stays intact.               ║
# ║                                                                            ║
# ║  HOW it runs:                                                              ║
# ║    Registered in ~/.claude.json as a stdio MCP server, launched via `uv`   ║
# ║    with Python pinned to 3.12 (barn's system python3.14 has no SD/ML       ║
# ║    wheels yet; same pin as the qdrant MCP). PEP 723 header above = self-   ║
# ║    contained deps, uv installs them on first run.                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝
"""SwarmUI MCP bridge: status, model listing, and text-to-image generation."""

import os
from urllib.parse import quote

import httpx
from mcp.server.fastmcp import FastMCP, Image

# WHERE SwarmUI listens. 127.0.0.1 on purpose — localhost-only bridge.
SWARM_URL = os.environ.get("SWARMUI_URL", "http://127.0.0.1:7801")

# WHERE SwarmUI writes finished images on disk (its OutputPath). The API hands
# back "View/..."-style paths; we swap the leading "View" for this root to tell
# the user the real on-disk location. Overridable if the OutputPath ever moves.
OUTPUT_ROOT = os.environ.get("SWARMUI_OUTPUT_ROOT", "/srv/ai/stable-diffusion/outputs")

# HTTP read timeout for generation. SDXL on the 3060 is ~8-15s, but batches or
# big sizes take longer — 300s gives comfortable headroom without hanging forever.
GEN_TIMEOUT = 300

mcp = FastMCP("swarmui")


# ── Session plumbing ────────────────────────────────────────────────────────
# Every route except GetNewSession needs a session_id. We cache one and, per the
# API contract, transparently re-fetch it once if it ever goes stale
# (error_id == "invalid_session_id"). Callers never see the session at all.
_session = {"id": None}


def _get_session(client: httpx.Client) -> str:
    _session["id"] = client.post("/API/GetNewSession", json={}).json()["session_id"]
    return _session["id"]


def _api(client: httpx.Client, route: str, payload: dict) -> dict:
    """POST to /API/<route> with the cached session, retrying once if it's stale."""
    if not _session["id"]:
        _get_session(client)
    body = {"session_id": _session["id"], **payload}
    data = client.post(f"/API/{route}", json=body).json()
    if data.get("error_id") == "invalid_session_id":
        _get_session(client)
        body["session_id"] = _session["id"]
        data = client.post(f"/API/{route}", json=body).json()
    return data


# ── Tools ───────────────────────────────────────────────────────────────────
@mcp.tool()
def swarmui_status() -> str:
    """Check whether SwarmUI is running and reachable on barn.

    Returns the running version if up, or a friendly hint to start it if not.
    Only calls GetNewSession, so a success here proves the whole wire is intact.
    """
    try:
        with httpx.Client(base_url=SWARM_URL, timeout=5) as c:
            d = c.post("/API/GetNewSession", json={}).json()
        return (
            f"✅ SwarmUI is up at {SWARM_URL}\n"
            f"   version:   {d.get('version')}\n"
            f"   server_id: {d.get('server_id')}\n"
            f"   user_id:   {d.get('user_id')}"
        )
    except Exception as e:
        return (
            f"❌ SwarmUI not reachable at {SWARM_URL}.\n"
            f"   Start it on barn with the `swarmui` command, then retry.\n"
            f"   (underlying error: {type(e).__name__}: {e})"
        )


@mcp.tool()
def list_models(subtype: str = "Stable-Diffusion", filter: str = "", depth: int = 3) -> str:
    """List models SwarmUI offers, with their architecture.

    subtype: which kind to list — "Stable-Diffusion" (checkpoints), "LoRA",
             "VAE", "Embedding", "ControlNet", "Wildcards", etc.
    filter:  optional case-insensitive substring to narrow the list
             (e.g. "pony", "flux", "cyber").
    Returns one "name  |  arch" per line — the `name` is exactly what the
    `model` argument of generate_image expects.
    """
    try:
        with httpx.Client(base_url=SWARM_URL, timeout=30) as c:
            d = _api(c, "ListModels", {
                "path": "", "depth": depth, "subtype": subtype, "dataImages": False,
            })
    except Exception as e:
        return f"❌ Could not list models — is SwarmUI up? ({type(e).__name__}: {e})"

    files = d.get("files", [])
    rows = []
    for f in files:
        name = f.get("name", "")
        if filter and filter.lower() not in name.lower():
            continue
        rows.append(f"{name}  |  {f.get('architecture', '?')}")
    if not rows:
        return f"(no {subtype} models" + (f" matching '{filter}'" if filter else "") + ")"
    header = f"{len(rows)} {subtype} model(s)" + (f" matching '{filter}'" if filter else "") + ":\n"
    return header + "\n".join(rows)


@mcp.tool()
def generate_image(
    prompt: str,
    model: str = "",
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    steps: int = 20,
    cfg_scale: float = 6.0,
    seed: int = -1,
    images: int = 1,
    extra_params: dict | None = None,
) -> list:
    """Generate image(s) with SwarmUI and return them inline so Claude can see them.

    prompt:          the positive text prompt.
    model:           checkpoint name from list_models (empty = SwarmUI's current default).
    negative_prompt: things to avoid.
    width/height:    pixel size (SDXL likes 1024x1024).
    steps:           sampling steps (~20 typical; 6-8 for fast previews).
    cfg_scale:       prompt adherence (SDXL ~4-7).
    seed:            -1 = random; a fixed int reproduces / lets you vary one knob.
    images:          how many to make in the batch (keep small — each returns inline).
    extra_params:    passthrough dict for ANY other SwarmUI T2I parameter — LoRAs,
                     sampler, refiner, controlnet, vae, etc. Keys use SwarmUI's own
                     names (see ListT2IParams). This is the "full reach" escape hatch.

    Returns a list of the generated image(s) plus a text note with on-disk paths.
    """
    # Flat body: SwarmUI wants all T2I params at the same level as session_id/images
    # (the docs' "rawInput" is conceptual, not a literal wrapper key).
    body = {
        "images": images,
        "prompt": prompt,
        "negativeprompt": negative_prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "cfgscale": cfg_scale,
        "seed": seed,
    }
    if model:
        body["model"] = model
    if extra_params:
        body.update(extra_params)

    try:
        with httpx.Client(base_url=SWARM_URL, timeout=GEN_TIMEOUT) as c:
            d = _api(c, "GenerateText2Image", body)
            if d.get("error"):
                return [f"❌ SwarmUI error: {d['error']}"]
            paths = d.get("images", [])
            if not paths:
                return [f"❌ No image returned. Raw reply: {d}"]

            out: list = []
            disk_paths = []
            for p in paths:
                # Fetch the rendered PNG bytes over the View endpoint (config-
                # independent, handles spaces via URL-encoding).
                img_bytes = c.get(f"/{quote(p, safe='/')}").content
                out.append(Image(data=img_bytes, format="png"))
                # Best-effort on-disk location for the user: View/... -> OUTPUT_ROOT/...
                disk_paths.append(p.replace("View", OUTPUT_ROOT, 1))
    except Exception as e:
        return [f"❌ Generation failed — is SwarmUI up? ({type(e).__name__}: {e})"]

    note = "🖼️ Generated {n} image(s), saved on barn at:\n{paths}".format(
        n=len(disk_paths), paths="\n".join(f"   {dp}" for dp in disk_paths)
    )
    out.append(note)
    return out


if __name__ == "__main__":
    # Speaks the MCP protocol over stdio — Claude Code launches this process
    # and talks to it through stdin/stdout. No network port of our own.
    mcp.run()

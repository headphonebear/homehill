#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════╗
# ║ bloom — SwarmUI launcher (barn)                                       ║
# ╠══════════════════════════════════════════════════════════════════════╣
# ║ Started by bloom.service (autostart since 2026-10-17) as user `ai`,   ║
# ║ with --launch_mode none. Runs in the FOREGROUND so systemd owns the   ║
# ║ process; SIGINT (= Ctrl+C) is SwarmUI's orderly shutdown.             ║
# ║ Can still be run by hand for debugging — stop the service first:     ║
# ║   sudo systemctl stop bloom && /srv/ai/SwarmUI/start-swarmui.sh       ║
# ║ Lives at /srv/ai/SwarmUI/start-swarmui.sh (untracked in the SwarmUI   ║
# ║ clone); this copy in Git is the source of truth.                      ║
# ║                                                                       ║
# ║ History: written 2026-07-19 as an on-demand launcher ("no autostart,  ║
# ║ Ctrl+C frees VRAM"). Since bloom became a service, VRAM is freed by   ║
# ║ SwarmUI itself (ClearVRAMAfterMinutes: 10) — see README.md.           ║
# ╚══════════════════════════════════════════════════════════════════════╝

set -euo pipefail

SWARM_DIR=/srv/ai/SwarmUI

# WHY: python3.12 (uv-managed, in the shared dir) MUST come before barn's
# system Python 3.14 on PATH. Matters if SwarmUI ever (re)installs the
# ComfyUI backend — 3.14 breaks the torch/xformers deps. In normal operation
# the venv uses its own absolute Python path anyway; this is the safety net.
export PATH="$SWARM_DIR/pybin:$PATH"

cd "$SWARM_DIR"
echo "SwarmUI starting …  UI: http://localhost:7801 (via bloom.homehill.de in Homehill)"

# launch-linux.sh builds if needed and starts the server. Arguments are passed
# through — bloom.service passes --launch_mode none (no browser on a service).
exec ./launch-linux.sh "$@"

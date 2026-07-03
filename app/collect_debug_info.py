from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

from beta_status import beta_status
from pgx_next_steps import pgx_next_steps
from verification_readiness import verification_readiness

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str]) -> str:
    try:
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20, cwd=ROOT)
        out = proc.stdout or ""
        return f"$ {' '.join(cmd)}\nexit code: {proc.returncode}\n{out.strip()}"
    except FileNotFoundError as exc:
        return f"$ {' '.join(cmd)}\nnot found: {exc}"
    except subprocess.TimeoutExpired:
        return f"$ {' '.join(cmd)}\ntimeout"


def collect_debug_info() -> str:
    lines = ["# Musubi LoRA Factory Debug Info", ""]
    lines.append(f"Python: {sys.version.split()[0]}")
    lines.append(f"Platform: {platform.platform()}")
    lines.append(f"Root: {ROOT}")
    lines.append("")
    lines.append("## Git")
    lines.append(_run(["git", "rev-parse", "--short", "HEAD"]))
    lines.append(_run(["git", "status", "--short"]))
    lines.append("")
    lines.append("## NVIDIA")
    lines.append(_run(["nvidia-smi"]))
    lines.append("")
    lines.append("## Beta status")
    lines.append(beta_status())
    lines.append("")
    lines.append("## Verification readiness")
    lines.append(verification_readiness())
    lines.append("")
    lines.append("## PGX next steps")
    lines.append(pgx_next_steps())
    return "\n".join(lines)


def main() -> int:
    print(collect_debug_info())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

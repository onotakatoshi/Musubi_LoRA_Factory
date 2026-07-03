from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "collect_debug_info.sh"
MODULE = ROOT / "app" / "collect_debug_info.py"


def main() -> int:
    script = SCRIPT.read_text(encoding="utf-8")
    module = MODULE.read_text(encoding="utf-8")
    assert script.startswith("#!/usr/bin/env bash")
    assert "set -euo pipefail" in script
    assert "python app/collect_debug_info.py" in script
    assert "def collect_debug_info" in module
    assert "beta_status()" in module
    assert "verification_readiness()" in module
    assert "nvidia-smi" in module
    print("Debug info static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

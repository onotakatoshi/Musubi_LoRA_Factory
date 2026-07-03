from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "scripts" / "verify_pgx_beta.sh"


def main() -> int:
    text = VERIFY.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash")
    assert "set -euo pipefail" in text
    assert "bash ./scripts/setup.sh" in text
    assert "bash ./scripts/check.sh" in text
    assert "bash ./scripts/check_beta.sh" in text
    assert "python app/verification_readiness.py" in text
    assert "PGX beta verification checks passed" in text
    print("PGX beta verification script static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

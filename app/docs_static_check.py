from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "pgx_beta_runbook.md"
ACCEPTANCE = ROOT / "docs" / "v1_acceptance_checklist.md"


def main() -> int:
    runbook = RUNBOOK.read_text(encoding="utf-8")
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")

    assert "https://github.com/onotakatoshi/Musubi_LoRA_Factory.git" in runbook
    assert "onotatoshi" not in runbook
    assert "verify_pgx_beta.sh" in runbook
    assert "Command Path Guard" in runbook
    assert "コピー前チェック" in runbook
    assert "READY: PGX実機でZ-Image LoRAの通し検証に進めます。" in runbook

    assert "Musubi Runtime Check" in acceptance
    assert "command path guard" in acceptance.lower()
    assert "export validation" in acceptance

    print("Docs static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

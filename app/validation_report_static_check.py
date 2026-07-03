from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app" / "validation_report.py"
SCRIPT = ROOT / "scripts" / "validation_report.sh"
TEST = ROOT / "app" / "validation_report_test.py"


def main() -> int:
    module = MODULE.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
    test = TEST.read_text(encoding="utf-8")
    assert "def validation_report" in module
    assert "find_latest_lora" in module
    assert "Latest log" in module
    assert "python app/validation_report.py" in script
    assert "Validation report test OK" in test
    print("Validation report static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

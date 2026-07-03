from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app" / "create_sample_dataset.py"


def main() -> int:
    text = MODULE.read_text(encoding="utf-8")
    assert "from PIL import Image" in text
    assert "def create_sample_dataset" in text
    assert ".png" in text
    assert ".txt" in text
    assert "sample blue eye" in text
    print("Sample dataset static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

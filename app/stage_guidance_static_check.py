from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAINING_ENGINE = ROOT / "app" / "training_engine.py"


def main() -> int:
    text = TRAINING_ENGINE.read_text(encoding="utf-8")
    assert "from stage_guidance import guidance_for_stage, success_guidance_for_stage" in text
    assert "guidance_for_stage" in text
    assert "success_guidance_for_stage" in text
    assert "===== FAILED" in text
    assert "===== DONE" in text
    print("Stage guidance static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

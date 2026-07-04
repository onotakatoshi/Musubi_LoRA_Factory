from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_desktop_launch.sh"
TEST = ROOT / "app" / "desktop_launch_smoke_test.py"
LAUNCHER = ROOT / "app" / "desktop_launcher.py"
FONT = ROOT / "app" / "ui_font.py"
NEXT_STEPS = ROOT / "app" / "pgx_next_steps.py"


def main() -> int:
    script = SCRIPT.read_text(encoding="utf-8")
    test = TEST.read_text(encoding="utf-8")
    launcher = LAUNCHER.read_text(encoding="utf-8")
    font = FONT.read_text(encoding="utf-8")
    next_steps = NEXT_STEPS.read_text(encoding="utf-8")
    assert script.startswith("#!/usr/bin/env bash")
    assert "set -euo pipefail" in script
    assert "python app/desktop_launch_smoke_test.py" in script
    assert "QT_QPA_PLATFORM" in test
    assert "DesktopApp" in test
    assert "QTabWidget" in test
    assert "apply_balanced_ui_font" in test
    assert "apply_balanced_ui_font" in launcher
    assert "Noto Sans CJK JP" in font
    assert "font-weight: 400" in font
    assert "check_desktop_launch.sh" in next_steps
    print("Desktop launch static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

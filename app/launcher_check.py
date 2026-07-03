from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SCRIPTS = [
    "scripts/setup.sh",
    "scripts/start.sh",
    "scripts/start_desktop.sh",
    "scripts/check.sh",
    "scripts/update.sh",
    "scripts/create_desktop_launcher.sh",
]


def main() -> int:
    missing = []
    for rel in REQUIRED_SCRIPTS:
        path = ROOT / rel
        if not path.exists():
            missing.append(rel)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        assert text.startswith("#!/usr/bin/env bash"), f"Missing bash shebang: {rel}"
        assert "set -euo pipefail" in text, f"Missing strict shell mode: {rel}"
    assert not missing, f"Missing launcher scripts: {missing}"

    desktop_script = ROOT / "scripts" / "create_desktop_launcher.sh"
    desktop_text = desktop_script.read_text(encoding="utf-8")
    assert "Musubi LoRA Factory.desktop" in desktop_text
    assert "start_desktop.sh" in desktop_text
    assert "Allow Launching" in desktop_text

    start_text = (ROOT / "scripts" / "start.sh").read_text(encoding="utf-8")
    start_desktop_text = (ROOT / "scripts" / "start_desktop.sh").read_text(encoding="utf-8")
    for text in [start_text, start_desktop_text]:
        assert "settings.example.toml" in text
        assert "startup_check.py" in text
        assert "desktop_main.py" in text

    print("Launcher check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

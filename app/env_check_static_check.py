from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_CHECK = ROOT / "app" / "env_check.py"
DESKTOP_MAIN = ROOT / "app" / "desktop_main.py"


def main() -> int:
    env_text = ENV_CHECK.read_text(encoding="utf-8")
    assert "from verification_readiness import verification_readiness" in env_text
    assert "## Verification readiness" in env_text
    assert "verification_readiness()" in env_text
    assert "NOT READY" in env_text

    desktop_text = DESKTOP_MAIN.read_text(encoding="utf-8")
    assert "check_environment(SETTINGS_PATH)" in desktop_text
    assert "self.system_log.setPlainText(check_environment(SETTINGS_PATH))" in desktop_text

    print("Environment check static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

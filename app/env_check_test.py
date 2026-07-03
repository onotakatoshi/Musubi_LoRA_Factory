from __future__ import annotations

import tempfile
from pathlib import Path

from env_check import check_environment


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        missing_settings = Path(tmp) / "missing-settings.toml"
        report = check_environment(missing_settings)
        assert report.startswith("# Environment Check")
        assert "## Verification readiness" in report
        assert "# Verification Readiness" in report
        assert "settings.toml not found" in report

    print("Environment check test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

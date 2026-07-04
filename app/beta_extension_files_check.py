from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "app/desktop_launcher.py",
    "app/ui_font.py",
    "app/desktop_launch_smoke_test.py",
    "app/desktop_launch_static_check.py",
    "app/env_check_test.py",
    "app/docs_static_check.py",
    "app/validation_report.py",
    "app/validation_report_static_check.py",
    "app/validation_report_test.py",
    "app/create_sample_dataset.py",
    "app/create_sample_dataset_static_check.py",
    "app/beta_extension_files_check.py",
    "app/collect_debug_info.py",
    "app/collect_debug_info_static_check.py",
    "app/pgx_next_steps.py",
    "scripts/check_desktop_launch.sh",
    "scripts/create_sample_dataset.sh",
    "scripts/collect_debug_info.sh",
    "scripts/validation_report.sh",
]


def main() -> int:
    missing = [rel for rel in FILES if not (ROOT / rel).exists()]
    assert not missing, f"Missing beta extension files: {missing}"
    print("Beta extension files check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path

from model_registry import enabled_profiles, profile_ids
from model_adapters import adapter_ids

ROOT = Path(__file__).resolve().parents[1]


def exists(rel: str) -> str:
    path = ROOT / rel
    return "OK" if path.exists() else "MISSING"


def beta_status() -> str:
    lines = ["# Beta Status", ""]
    lines.append("## Scope")
    lines.append("Ver 1.0 beta target: Z-Image / Z-Image-Turbo")
    lines.append(f"Enabled profiles: {', '.join(profile_ids())}")
    lines.append(f"Implemented adapters: {', '.join(adapter_ids())}")
    lines.append("")
    lines.append("## Required files")
    for rel in [
        "app/desktop_main.py",
        "app/model_registry.py",
        "app/model_adapters.py",
        "app/model_ui.py",
        "app/command_preview.py",
        "app/preflight.py",
        "app/env_check.py",
        "app/startup_check.py",
        "app/launcher_check.py",
        "app/command_preview_test.py",
        "app/project_roundtrip_test.py",
        "scripts/setup.sh",
        "scripts/start.sh",
        "scripts/start_desktop.sh",
        "scripts/check.sh",
        "scripts/update.sh",
        "scripts/create_desktop_launcher.sh",
        "docs/pgx_beta_runbook.md",
        "docs/v1_acceptance_checklist.md",
        "docs/model_expansion_checklist.md",
    ]:
        lines.append(f"- {exists(rel)} {rel}")
    lines.append("")
    lines.append("## Next PGX action")
    lines.append("1. ./scripts/update.sh")
    lines.append("2. ./scripts/check.sh")
    lines.append("3. ./scripts/start.sh or desktop icon")
    lines.append("4. Follow docs/pgx_beta_runbook.md")
    return "\n".join(lines)


if __name__ == "__main__":
    print(beta_status())

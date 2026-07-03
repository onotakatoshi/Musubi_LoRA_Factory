from __future__ import annotations

from pathlib import Path

from model_registry import profile_ids
from model_adapters import adapter_ids

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "app/desktop_main.py",
    "app/desktop_static_check.py",
    "app/model_registry.py",
    "app/model_adapters.py",
    "app/model_ui.py",
    "app/command_preview.py",
    "app/command_path_guard.py",
    "app/command_path_guard_test.py",
    "app/stage_guidance.py",
    "app/stage_guidance_test.py",
    "app/preflight.py",
    "app/env_check.py",
    "app/musubi_runtime_check.py",
    "app/startup_check.py",
    "app/launcher_check.py",
    "app/command_preview_test.py",
    "app/project_roundtrip_test.py",
    "app/training_engine.py",
    "app/training_engine_test.py",
    "app/output_detector.py",
    "app/output_detector_test.py",
    "app/find_lora_output.py",
    "app/export_validator.py",
    "app/export_validator_test.py",
    "app/verification_readiness.py",
    "app/verification_readiness_test.py",
    "scripts/setup.sh",
    "scripts/start.sh",
    "scripts/start_desktop.sh",
    "scripts/check.sh",
    "scripts/check_beta.sh",
    "scripts/update.sh",
    "scripts/create_desktop_launcher.sh",
    "docs/pgx_beta_runbook.md",
    "docs/v1_acceptance_checklist.md",
    "docs/model_expansion_checklist.md",
]


def exists(rel: str) -> str:
    path = ROOT / rel
    return "OK" if path.exists() else "MISSING"


def missing_required_files() -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (ROOT / rel).exists()]


def beta_status() -> str:
    lines = ["# Beta Status", ""]
    lines.append("## Scope")
    lines.append("Ver 1.0 beta target: Z-Image / Z-Image-Turbo")
    lines.append(f"Enabled profiles: {', '.join(profile_ids())}")
    lines.append(f"Implemented adapters: {', '.join(adapter_ids())}")
    lines.append("")
    lines.append("## Core engine")
    lines.append("- TrainingEngine: Latent Cache / Text Cache / Train")
    lines.append("- CommandPathGuard: final path validation before run")
    lines.append("- StageGuidance: success/failure next actions in run log")
    lines.append("- MusubiRuntimeCheck: configured musubi python / accelerate / scripts check")
    lines.append("- OutputDetector: latest LoRA .safetensors detection")
    lines.append("- ExportValidator: pre-copy validation for ComfyUI export")
    lines.append("- VerificationReadiness: PGX実機検証へ進める状態か判定")
    lines.append("")
    lines.append("## Required files")
    for rel in REQUIRED_FILES:
        lines.append(f"- {exists(rel)} {rel}")
    lines.append("")
    missing = missing_required_files()
    lines.append("## Result")
    if missing:
        lines.append("NG: missing required files")
        lines.extend(f"- {rel}" for rel in missing)
    else:
        lines.append("OK: required beta files exist")
    lines.append("")
    lines.append("## Next PGX action")
    lines.append("1. ./scripts/update.sh")
    lines.append("2. ./scripts/check.sh")
    lines.append("3. ./scripts/check_beta.sh")
    lines.append("4. python app/verification_readiness.py")
    lines.append("5. ./scripts/start.sh or desktop icon")
    lines.append("6. Follow docs/pgx_beta_runbook.md")
    return "\n".join(lines)


if __name__ == "__main__":
    missing = missing_required_files()
    print(beta_status())
    raise SystemExit(1 if missing else 0)

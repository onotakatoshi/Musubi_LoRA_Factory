from __future__ import annotations

from pathlib import Path

from beta_status import missing_required_files

ROOT = Path(__file__).resolve().parents[1]

READINESS_FILES = {
    "desktop": ROOT / "app" / "desktop_main.py",
    "commands": ROOT / "app" / "commands.py",
    "training_engine": ROOT / "app" / "training_engine.py",
    "command_path_guard": ROOT / "app" / "command_path_guard.py",
    "stage_guidance": ROOT / "app" / "stage_guidance.py",
    "export_validator": ROOT / "app" / "export_validator.py",
    "verify_script": ROOT / "scripts" / "verify_pgx_beta.sh",
    "check_beta": ROOT / "scripts" / "check_beta.sh",
    "runbook": ROOT / "docs" / "pgx_beta_runbook.md",
    "acceptance": ROOT / "docs" / "v1_acceptance_checklist.md",
}


def _contains(path: Path, needle: str) -> bool:
    return path.exists() and needle in path.read_text(encoding="utf-8")


def is_ready_report(report: str) -> bool:
    return "READY: PGX実機でZ-Image LoRAの通し検証に進めます。" in report and "NOT READY:" not in report


def verification_readiness() -> str:
    lines = ["# Verification Readiness", ""]
    blockers: list[str] = []

    missing = missing_required_files()
    if missing:
        blockers.append("missing required beta files")
        lines.append("NG: missing required beta files")
        lines.extend(f"- {rel}" for rel in missing)
    else:
        lines.append("OK: required beta files exist")

    checks = [
        ("Desktop uses TrainingEngine", READINESS_FILES["desktop"], "self.training_engine = TrainingEngine()"),
        ("Desktop has full pipeline button", READINESS_FILES["desktop"], "全部実行"),
        ("Desktop auto-detects LoRA", READINESS_FILES["desktop"], "find_latest_lora"),
        ("Desktop wires export validation", READINESS_FILES["desktop"], "validate_lora_for_export"),
        ("Commands use musubi python accelerate module", READINESS_FILES["commands"], "accelerate.commands.launch"),
        ("Commands include Z-Image latent cache", READINESS_FILES["commands"], "zimage_cache_latents.py"),
        ("Commands include Z-Image text cache", READINESS_FILES["commands"], "zimage_cache_text_encoder_outputs.py"),
        ("Commands include Z-Image train", READINESS_FILES["commands"], "zimage_train_network.py"),
        ("Training engine uses command path guard", READINESS_FILES["training_engine"], "command_paths_ok"),
        ("Training engine saves logs", READINESS_FILES["training_engine"], "infer_log_dir_from_sections"),
        ("Training engine handles startup errors", READINESS_FILES["training_engine"], "errorOccurred.connect"),
        ("Training engine supports force kill", READINESS_FILES["training_engine"], "kill()"),
        ("Training engine sets unbuffered logs", READINESS_FILES["training_engine"], "PYTHONUNBUFFERED"),
        ("Training engine emits stage guidance", READINESS_FILES["training_engine"], "guidance_for_stage"),
        ("Training engine emits success guidance", READINESS_FILES["training_engine"], "success_guidance_for_stage"),
        ("Command path guard checks cwd", READINESS_FILES["command_path_guard"], "cwd not found"),
        ("Command path guard checks python", READINESS_FILES["command_path_guard"], "python not found"),
        ("Command path guard checks script", READINESS_FILES["command_path_guard"], "script not found"),
        ("Stage guidance covers train", READINESS_FILES["stage_guidance"], "train"),
        ("Stage guidance tells next checks", READINESS_FILES["stage_guidance"], "次に確認すること"),
        ("Export validator returns OK", READINESS_FILES["export_validator"], "Result: OK"),
        ("Export validator blocks missing ComfyUI folder", READINESS_FILES["export_validator"], "LoRAフォルダが存在しません"),
        ("PGX verify script runs setup", READINESS_FILES["verify_script"], "bash ./scripts/setup.sh"),
        ("PGX verify script runs check", READINESS_FILES["verify_script"], "bash ./scripts/check.sh"),
        ("PGX verify script runs beta check", READINESS_FILES["verify_script"], "bash ./scripts/check_beta.sh"),
        ("PGX verify script runs readiness", READINESS_FILES["verify_script"], "verification_readiness.py"),
        ("Beta check compiles desktop", READINESS_FILES["check_beta"], "app/desktop_main.py"),
        ("Beta check runs static check", READINESS_FILES["check_beta"], "desktop_static_check.py"),
        ("Beta check runs command path guard test", READINESS_FILES["check_beta"], "command_path_guard_test.py"),
        ("Beta check runs stage guidance test", READINESS_FILES["check_beta"], "stage_guidance_test.py"),
        ("Beta check runs musubi runtime test", READINESS_FILES["check_beta"], "musubi_runtime_check_test.py"),
        ("Beta check runs verify script static check", READINESS_FILES["check_beta"], "verify_pgx_beta_static_check.py"),
        ("Beta check runs export validator test", READINESS_FILES["check_beta"], "export_validator_test.py"),
        ("Runbook documents command path guard", READINESS_FILES["runbook"], "Command Path Guard"),
        ("Runbook documents export validation", READINESS_FILES["runbook"], "コピー前チェック"),
        ("Acceptance checklist includes runtime check", READINESS_FILES["acceptance"], "Musubi Runtime Check"),
        ("Acceptance checklist includes export validation", READINESS_FILES["acceptance"], "export validation"),
    ]

    lines.append("")
    lines.append("## Checks")
    for label, path, needle in checks:
        if _contains(path, needle):
            lines.append(f"OK: {label}")
        else:
            blockers.append(label)
            lines.append(f"NG: {label}")

    lines.append("")
    lines.append("## Result")
    if blockers:
        lines.append("NOT READY: PGX実機検証の前に修正が必要です。")
        lines.extend(f"- {item}" for item in blockers)
    else:
        lines.append("READY: PGX実機でZ-Image LoRAの通し検証に進めます。")
        lines.append("Next: bash ./scripts/verify_pgx_beta.sh をPGXで通してからGUIで実データ検証してください。")
    return "\n".join(lines)


if __name__ == "__main__":
    report = verification_readiness()
    print(report)
    raise SystemExit(0 if is_ready_report(report) else 1)

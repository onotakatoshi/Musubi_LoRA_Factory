from __future__ import annotations

import shlex
from pathlib import Path

from training_engine import TrainingStage

PATH_FLAGS = {
    "--dataset_config": "file",
    "--vae": "file",
    "--dit": "file",
    "--text_encoder": "file",
    "--base_weights": "file",
    "--output_dir": "dir_parent",
}


def _extract_flag_values(command: str) -> list[tuple[str, str, str]]:
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        return [("__parse_error__", str(exc), "error")]
    found: list[tuple[str, str, str]] = []
    for i, token in enumerate(tokens):
        if token in PATH_FLAGS and i + 1 < len(tokens):
            found.append((token, tokens[i + 1], PATH_FLAGS[token]))
        elif any(token.startswith(flag + "=") for flag in PATH_FLAGS):
            flag, value = token.split("=", 1)
            found.append((flag, value, PATH_FLAGS[flag]))
    return found


def validate_command_paths(sections: dict[str, str]) -> str:
    lines = ["# Command Path Guard", ""]
    errors: list[str] = []
    for stage in [TrainingStage.LATENT_CACHE.value, TrainingStage.TEXT_CACHE.value, TrainingStage.TRAIN.value]:
        command = sections.get(stage, "")
        if not command:
            errors.append(f"{stage}: command is empty")
            continue
        lines.append(f"## {stage}")
        for flag, value, kind in _extract_flag_values(command):
            if flag == "__parse_error__":
                errors.append(f"{stage}: command parse error: {value}")
                lines.append(f"NG: parse error: {value}")
                continue
            path = Path(value)
            if kind == "file":
                if not path.exists() or not path.is_file():
                    errors.append(f"{stage}: {flag} not found: {path}")
                    lines.append(f"NG: {flag}: {path}")
                else:
                    lines.append(f"OK: {flag}: {path}")
            elif kind == "dir_parent":
                parent = path.parent
                if not parent.exists():
                    errors.append(f"{stage}: parent directory not found for {flag}: {parent}")
                    lines.append(f"NG: {flag} parent missing: {parent}")
                else:
                    lines.append(f"OK: {flag}: {path}")
        lines.append("")
    if errors:
        return "\n".join(lines) + "\nResult: NG\n" + "\n".join(f"- {e}" for e in errors)
    return "\n".join(lines) + "\nResult: OK"


def command_paths_ok(sections: dict[str, str]) -> tuple[bool, str]:
    report = validate_command_paths(sections)
    return ("Result: OK" in report, report)

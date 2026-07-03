from __future__ import annotations

import shlex
from pathlib import Path

STAGES = ["latent_cache", "text_cache", "train"]

PATH_FLAGS = {
    "--dataset_config": "file",
    "--vae": "file",
    "--dit": "file",
    "--text_encoder": "file",
    "--base_weights": "file",
    "--output_dir": "dir_parent",
}


def _split_tokens(command: str) -> tuple[list[str], str | None]:
    try:
        return shlex.split(command), None
    except ValueError as exc:
        return [], str(exc)


def _extract_cwd(tokens: list[str]) -> Path | None:
    for i, token in enumerate(tokens):
        if token == "cd" and i + 1 < len(tokens):
            return Path(tokens[i + 1])
    return None


def _tokens_after_shell_and(tokens: list[str]) -> list[str]:
    if "&&" in tokens:
        index = tokens.index("&&")
        return tokens[index + 1 :]
    return tokens


def _extract_flag_values(tokens: list[str]) -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    for i, token in enumerate(tokens):
        if token in PATH_FLAGS and i + 1 < len(tokens):
            found.append((token, tokens[i + 1], PATH_FLAGS[token]))
        elif any(token.startswith(flag + "=") for flag in PATH_FLAGS):
            flag, value = token.split("=", 1)
            found.append((flag, value, PATH_FLAGS[flag]))
    return found


def _validate_command_entry(stage: str, command: str) -> tuple[list[str], list[str]]:
    lines: list[str] = []
    errors: list[str] = []
    tokens, parse_error = _split_tokens(command)
    if parse_error:
        errors.append(f"{stage}: command parse error: {parse_error}")
        lines.append(f"NG: parse error: {parse_error}")
        return lines, errors

    cwd = _extract_cwd(tokens)
    if cwd is not None:
        if cwd.exists() and cwd.is_dir():
            lines.append(f"OK: cwd: {cwd}")
        else:
            errors.append(f"{stage}: cwd not found: {cwd}")
            lines.append(f"NG: cwd: {cwd}")

    run_tokens = _tokens_after_shell_and(tokens)
    if run_tokens:
        python_path = Path(run_tokens[0])
        if python_path.is_absolute():
            if python_path.exists() and python_path.is_file():
                lines.append(f"OK: python: {python_path}")
            else:
                errors.append(f"{stage}: python not found: {python_path}")
                lines.append(f"NG: python: {python_path}")
        elif run_tokens[0] == "python" or run_tokens[0].startswith("python"):
            lines.append(f"OK: python command: {run_tokens[0]}")

        for token in run_tokens:
            if token.endswith(".py"):
                script = Path(token)
                candidates = [script]
                if cwd is not None and not script.is_absolute():
                    candidates.insert(0, cwd / script)
                if any(p.exists() and p.is_file() for p in candidates):
                    resolved = next(p for p in candidates if p.exists() and p.is_file())
                    lines.append(f"OK: script: {resolved}")
                else:
                    errors.append(f"{stage}: script not found: {token}")
                    lines.append(f"NG: script: {token}")
                break

    for flag, value, kind in _extract_flag_values(tokens):
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
    return lines, errors


def validate_command_paths(sections: dict[str, str]) -> str:
    lines = ["# Command Path Guard", ""]
    errors: list[str] = []
    for stage in STAGES:
        command = sections.get(stage, "")
        if not command:
            errors.append(f"{stage}: command is empty")
            continue
        lines.append(f"## {stage}")
        stage_lines, stage_errors = _validate_command_entry(stage, command)
        lines.extend(stage_lines)
        errors.extend(stage_errors)
        lines.append("")
    if errors:
        return "\n".join(lines) + "\nResult: NG\n" + "\n".join(f"- {e}" for e in errors)
    return "\n".join(lines) + "\nResult: OK"


def command_paths_ok(sections: dict[str, str]) -> tuple[bool, str]:
    report = validate_command_paths(sections)
    return ("Result: OK" in report, report)

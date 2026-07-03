from __future__ import annotations

from pathlib import Path

from output_detector import find_latest_lora, output_summary


def _latest_file(folder: Path, pattern: str) -> Path | None:
    if not folder.exists():
        return None
    files = [p for p in folder.rglob(pattern) if p.is_file()]
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def _tail(path: Path, lines: int = 40) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return f"Could not read log: {exc}"
    return "\n".join(text.splitlines()[-lines:])


def validation_report(output_dir: str | Path, output_name: str = "") -> str:
    out = Path(output_dir)
    logs_dir = out / "logs"
    latest_lora = find_latest_lora(out, output_name)
    latest_log = _latest_file(logs_dir, "*.log")
    lines = ["# Validation Report", ""]
    lines.append(f"Output dir: {out}")
    lines.append(f"Logs dir: {logs_dir}")
    lines.append("")
    lines.append("## LoRA")
    lines.append(output_summary(out, output_name))
    lines.append("")
    lines.append("## Latest log")
    if latest_log:
        lines.append(f"Latest log: {latest_log}")
        lines.append("")
        lines.append("```text")
        lines.append(_tail(latest_log))
        lines.append("```")
    else:
        lines.append("NG: log file not found")
    lines.append("")
    lines.append("## Result")
    if latest_lora and latest_log:
        lines.append("OK: LoRA and log were found. Next: 書き出しタブでコピー前チェックを実行してください。")
    elif latest_lora:
        lines.append("WARN: LoRA was found, but log file was not found.")
    else:
        lines.append("NG: LoRA was not found. 学習ログを確認してください。")
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a validation report for a Musubi LoRA Factory output folder.")
    parser.add_argument("output_dir")
    parser.add_argument("--name", default="")
    args = parser.parse_args()
    print(validation_report(args.output_dir, args.name))

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def logs_dir(root: Path) -> Path:
    path = root / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def make_log_path(root: Path, section: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_section = section.replace("/", "_").replace(" ", "_")
    return logs_dir(root) / f"{stamp}_{safe_section}.log"


def save_log(root: Path, section: str, content: str) -> Path:
    path = make_log_path(root, section)
    path.write_text(content, encoding="utf-8")
    return path


def append_log(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line.rstrip("\n") + "\n")


def list_recent_logs(root: Path, limit: int = 20) -> list[Path]:
    d = logs_dir(root)
    return sorted(d.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def recent_logs_markdown(root: Path, limit: int = 10) -> str:
    logs = list_recent_logs(root, limit=limit)
    if not logs:
        return "ログファイルはまだありません。"
    lines = ["# Recent Logs", ""]
    for path in logs:
        stat = path.stat()
        size_kb = stat.st_size / 1024
        lines.append(f"- `{path.name}` — {size_kb:.1f} KB")
    lines.append("")
    lines.append(f"保存先: `{logs_dir(root)}`")
    return "\n".join(lines)

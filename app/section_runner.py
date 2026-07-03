from __future__ import annotations

from pathlib import Path
from typing import Generator

from runner import split_command_sections
from stream_runner import stream_shell_command


def get_section_command(command_preview: str, section: str) -> str:
    sections = split_command_sections(command_preview)
    return sections.get(section, "").strip()


def stream_section(command_preview: str, section: str, cwd: Path | None = None) -> Generator[str, None, None]:
    command = get_section_command(command_preview, section)
    if not command:
        yield f"NG: command section not found: {section}"
        return
    yield from stream_shell_command(command, cwd=cwd, job_id=section)

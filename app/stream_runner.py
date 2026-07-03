from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Generator

from log_store import append_log, make_log_path


_RUNNING: dict[str, subprocess.Popen[str]] = {}
_RUNNING_LOGS: dict[str, Path] = {}


def stream_shell_command(command: str, cwd: Path | None = None, job_id: str = "default") -> Generator[str, None, None]:
    """Run command and yield accumulated logs.

    Gradio consumes this generator to update a textbox while the command is running.
    The same output is also saved to logs/*.log.
    """
    if not command.strip():
        yield "NG: Empty command"
        return
    if job_id in _RUNNING and _RUNNING[job_id].poll() is None:
        yield f"NG: job is already running: {job_id}"
        return

    log_root = cwd if cwd else Path.cwd()
    log_path = make_log_path(log_root, job_id)
    _RUNNING_LOGS[job_id] = log_path

    log_lines: list[str] = [
        f"LOG FILE: {log_path}",
        f"START: {command}",
        "",
    ]
    for header_line in log_lines:
        append_log(log_path, header_line)

    proc = subprocess.Popen(
        command,
        shell=True,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    _RUNNING[job_id] = proc

    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            clean = line.rstrip("\n")
            log_lines.append(clean)
            append_log(log_path, clean)
            yield "\n".join(log_lines[-300:])
        code = proc.wait()
        footer = f"DONE: exit code {code}" if code == 0 else f"FAILED: exit code {code}"
        log_lines.append("")
        log_lines.append(footer)
        append_log(log_path, "")
        append_log(log_path, footer)
        yield "\n".join(log_lines[-400:])
    finally:
        _RUNNING.pop(job_id, None)
        _RUNNING_LOGS.pop(job_id, None)


def stop_job(job_id: str = "default") -> str:
    proc = _RUNNING.get(job_id)
    if proc is None or proc.poll() is not None:
        return f"No running job: {job_id}"
    log_path = _RUNNING_LOGS.get(job_id)
    proc.terminate()
    try:
        proc.wait(timeout=10)
        _RUNNING.pop(job_id, None)
        _RUNNING_LOGS.pop(job_id, None)
        if log_path:
            append_log(log_path, f"STOPPED: {job_id}")
        return f"Stopped job: {job_id}"
    except subprocess.TimeoutExpired:
        proc.kill()
        _RUNNING.pop(job_id, None)
        _RUNNING_LOGS.pop(job_id, None)
        if log_path:
            append_log(log_path, f"KILLED: {job_id}")
        return f"Killed job: {job_id}"


def is_running(job_id: str = "default") -> bool:
    proc = _RUNNING.get(job_id)
    return proc is not None and proc.poll() is None

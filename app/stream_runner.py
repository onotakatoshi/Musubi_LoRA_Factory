from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Generator


_RUNNING: dict[str, subprocess.Popen[str]] = {}


def stream_shell_command(command: str, cwd: Path | None = None, job_id: str = "default") -> Generator[str, None, None]:
    """Run command and yield accumulated logs.

    Gradio can consume this generator to update a textbox while the command is running.
    """
    if not command.strip():
        yield "NG: Empty command"
        return
    if job_id in _RUNNING and _RUNNING[job_id].poll() is None:
        yield f"NG: job is already running: {job_id}"
        return

    log_lines: list[str] = [f"START: {command}", ""]
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
            log_lines.append(line.rstrip("\n"))
            yield "\n".join(log_lines[-300:])
        code = proc.wait()
        if code == 0:
            log_lines.append("")
            log_lines.append(f"DONE: exit code {code}")
        else:
            log_lines.append("")
            log_lines.append(f"FAILED: exit code {code}")
        yield "\n".join(log_lines[-400:])
    finally:
        _RUNNING.pop(job_id, None)


def stop_job(job_id: str = "default") -> str:
    proc = _RUNNING.get(job_id)
    if proc is None or proc.poll() is not None:
        return f"No running job: {job_id}"
    proc.terminate()
    try:
        proc.wait(timeout=10)
        _RUNNING.pop(job_id, None)
        return f"Stopped job: {job_id}"
    except subprocess.TimeoutExpired:
        proc.kill()
        _RUNNING.pop(job_id, None)
        return f"Killed job: {job_id}"


def is_running(job_id: str = "default") -> bool:
    proc = _RUNNING.get(job_id)
    return proc is not None and proc.poll() is None

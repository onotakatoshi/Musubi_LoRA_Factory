from __future__ import annotations

import subprocess
from pathlib import Path


ZIMAGE_SCRIPTS = [
    "src/musubi_tuner/zimage_cache_latents.py",
    "src/musubi_tuner/zimage_cache_text_encoder_outputs.py",
    "src/musubi_tuner/zimage_train_network.py",
]


def _finish(lines: list[str]) -> str:
    text = "\n".join(lines)
    if "NG" in text:
        return text + "\n\nResult: NG. musubi-tuner repo / python / accelerate を確認してください。"
    return text + "\n\nResult: OK. musubi-tuner runtime is ready."


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 20) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        return proc.returncode, proc.stdout or ""
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, (exc.stdout or "") + "\ntimeout"


def check_musubi_runtime(musubi_python: str | Path, musubi_repo: str | Path, profile_id: str = "z-image") -> str:
    python_path = Path(musubi_python)
    repo = Path(musubi_repo)
    lines = ["# Musubi Runtime Check", "", f"profile: {profile_id}", ""]

    if not python_path.exists():
        lines.append(f"NG: musubi python not found: {python_path}")
        return _finish(lines)
    if not repo.exists():
        lines.append(f"NG: musubi repo not found: {repo}")
        return _finish(lines)

    code, out = _run([str(python_path), "--version"])
    lines.append(f"python --version: {'OK' if code == 0 else 'NG'}")
    if out.strip():
        lines.append(out.strip().splitlines()[0])

    code, out = _run([str(python_path), "-m", "accelerate.commands.launch", "--help"], cwd=repo)
    lines.append(f"accelerate module: {'OK' if code == 0 else 'NG'}")
    if code != 0:
        lines.append(out.strip()[:800])

    if profile_id == "z-image":
        lines.append("")
        lines.append("## Z-Image scripts")
        for rel in ZIMAGE_SCRIPTS:
            path = repo / rel
            lines.append(f"{'OK' if path.exists() else 'NG'}: {rel}")
    else:
        lines.append(f"NG: runtime check not implemented for profile: {profile_id}")

    return _finish(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python app/musubi_runtime_check.py /path/to/musubi/python /path/to/musubi-tuner")
        raise SystemExit(2)
    print(check_musubi_runtime(sys.argv[1], sys.argv[2]))

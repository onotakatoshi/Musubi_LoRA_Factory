from __future__ import annotations

import os
import tempfile
from pathlib import Path

from musubi_runtime_check import check_musubi_runtime


ZIMAGE_SCRIPTS = [
    "src/musubi_tuner/zimage_cache_latents.py",
    "src/musubi_tuner/zimage_cache_text_encoder_outputs.py",
    "src/musubi_tuner/zimage_train_network.py",
]


def _fake_python(path: Path, ok: bool = True) -> None:
    code = "#!/usr/bin/env bash\n"
    if ok:
        code += "echo 'Python 3.11.0'\nexit 0\n"
    else:
        code += "echo 'fake python failure'\nexit 1\n"
    path.write_text(code, encoding="utf-8")
    os.chmod(path, 0o755)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        missing = check_musubi_runtime(root / "missing-python", root / "repo")
        assert "musubi python not found" in missing
        assert "Result: NG" in missing

        py = root / "python"
        _fake_python(py)
        missing_repo = check_musubi_runtime(py, root / "missing-repo")
        assert "musubi repo not found" in missing_repo
        assert "Result: NG" in missing_repo

        repo = root / "musubi-tuner"
        repo.mkdir()
        no_scripts = check_musubi_runtime(py, repo)
        assert "accelerate module: OK" in no_scripts
        assert "NG: src/musubi_tuner/zimage_cache_latents.py" in no_scripts
        assert "Result: NG" in no_scripts

        for rel in ZIMAGE_SCRIPTS:
            p = repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# dummy\n", encoding="utf-8")
        ok = check_musubi_runtime(py, repo)
        assert "Result: OK" in ok

        bad_py = root / "bad-python"
        _fake_python(bad_py, ok=False)
        bad = check_musubi_runtime(bad_py, repo)
        assert "python --version: NG" in bad
        assert "accelerate module: NG" in bad
        assert "Result: NG" in bad

    print("Musubi runtime check test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

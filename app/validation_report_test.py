from __future__ import annotations

import tempfile
from pathlib import Path

from validation_report import validation_report


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        empty = validation_report(out, "eye_lora_zimage")
        assert "Validation Report" in empty
        assert "LoRA was not found" in empty

        logs = out / "logs"
        logs.mkdir()
        (logs / "001_train.log").write_text("line1\nline2\nDONE\n", encoding="utf-8")
        (out / "eye_lora_zimage.safetensors").write_bytes(b"dummy")
        ok = validation_report(out, "eye_lora_zimage")
        assert "OK: LoRA and log were found" in ok
        assert "Latest log" in ok
        assert "DONE" in ok

    print("Validation report test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

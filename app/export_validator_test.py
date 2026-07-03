from __future__ import annotations

import tempfile
from pathlib import Path

from export_validator import validate_lora_for_export


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        dest = root / "ComfyUI" / "models" / "loras"
        missing = validate_lora_for_export(root / "missing.safetensors", dest)
        assert missing.startswith("# Export Validation")
        assert "存在しません" in missing
        assert "Result: NG" in missing

        bad = root / "bad.txt"
        bad.write_text("x", encoding="utf-8")
        bad_result = validate_lora_for_export(bad, dest)
        assert ".safetensors" in bad_result
        assert "Result: NG" in bad_result

        lora = root / "eye_lora_zimage.safetensors"
        lora.write_bytes(b"dummy")
        dest_missing = validate_lora_for_export(lora, dest)
        assert "LoRAフォルダが存在しません" in dest_missing
        assert "Result: NG" in dest_missing

        dest.mkdir(parents=True)
        ok = validate_lora_for_export(lora, dest)
        assert "OK: Source" in ok
        assert "Overwrite: no" in ok
        assert "Result: OK" in ok

        (dest / lora.name).write_bytes(b"old")
        overwrite = validate_lora_for_export(lora, dest)
        assert "Overwrite: yes" in overwrite
        assert "Result: OK" in overwrite

    print("Export validator test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

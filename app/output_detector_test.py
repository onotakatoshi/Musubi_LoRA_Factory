from __future__ import annotations

import tempfile
import time
from pathlib import Path

from output_detector import find_latest_lora, output_summary


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        assert find_latest_lora(root) is None
        first = root / "first.safetensors"
        first.write_bytes(b"first")
        time.sleep(0.01)
        second = root / "eye_lora_zimage.safetensors"
        second.write_bytes(b"second")
        assert find_latest_lora(root) == second
        assert find_latest_lora(root, "eye_lora") == second
        assert find_latest_lora(root, "first") == first
        assert "OK:" in output_summary(root, "eye_lora")
        assert "NG:" in output_summary(root / "missing")
    print("Output detector test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

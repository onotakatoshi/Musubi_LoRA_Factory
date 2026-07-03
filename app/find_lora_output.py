from __future__ import annotations

import argparse
from pathlib import Path

from output_detector import find_latest_lora, output_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Find latest LoRA safetensors in an output directory")
    parser.add_argument("output_dir")
    parser.add_argument("--name", default="", help="Prefer files whose stem contains this output name")
    args = parser.parse_args()

    print(output_summary(Path(args.output_dir), args.name))
    return 0 if find_latest_lora(Path(args.output_dir), args.name) else 1


if __name__ == "__main__":
    raise SystemExit(main())

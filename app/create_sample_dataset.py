from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


CAPTION = "sample blue eye, simple validation image, clean caption"


def create_sample_dataset(output_dir: str | Path, count: int = 4) -> str:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for i in range(1, count + 1):
        img = Image.new("RGB", (768, 768), (235, 240, 255))
        draw = ImageDraw.Draw(img)
        cx, cy = 384, 384
        r = 150 + i * 8
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(230, 240, 255), outline=(40, 80, 140), width=8)
        draw.ellipse((cx - 95, cy - 95, cx + 95, cy + 95), fill=(60, 120, 210), outline=(20, 60, 120), width=6)
        draw.ellipse((cx - 38, cy - 38, cx + 38, cy + 38), fill=(15, 25, 40))
        draw.ellipse((cx - 45, cy - 70, cx - 5, cy - 30), fill=(245, 250, 255))
        name = f"sample_eye_{i:02d}"
        img.save(out / f"{name}.png")
        (out / f"{name}.txt").write_text(f"{CAPTION}, sample number {i}\n", encoding="utf-8")
    return f"Created {count} sample images with captions: {out}"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Create a tiny sample dataset for GUI validation.")
    parser.add_argument("output_dir")
    parser.add_argument("--count", type=int, default=4)
    args = parser.parse_args()
    print(create_sample_dataset(args.output_dir, args.count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

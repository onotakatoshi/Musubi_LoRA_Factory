from __future__ import annotations

from pathlib import Path

from pipeline import image_files

TARGET_HINTS = {
    "eye": ["eye", "eyes", "pupil", "iris", "eyelash", "eyelashes", "瞳", "目"],
    "mouth": ["mouth", "lips", "teeth", "smile", "tongue", "口", "唇"],
    "hair": ["hair", "bangs", "ponytail", "髪"],
    "hand": ["hand", "finger", "fingers", "手", "指"],
}

NOISE_WORDS = {
    "eye": ["background", "clothes", "shirt", "hair", "body", "full body"],
    "mouth": ["background", "clothes", "shirt", "hair", "full body"],
}


def _read_caption(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace").strip()


def diagnose_captions(dataset_dir: Path, lora_type: str = "eye", lang: str = "日本語") -> str:
    ja = lang != "English"
    imgs = image_files(dataset_dir)
    if not imgs:
        return "❌ 画像が見つかりません。" if ja else "❌ No images found."

    missing: list[str] = []
    empty: list[str] = []
    short: list[str] = []
    long: list[str] = []
    target_missing: list[str] = []
    noise_hits: list[str] = []
    total_words = 0
    caption_count = 0

    hints = TARGET_HINTS.get(lora_type, [])
    noise = NOISE_WORDS.get(lora_type, [])

    for img in imgs:
        txt = img.with_suffix(".txt")
        if not txt.exists():
            missing.append(img.name)
            continue
        cap = _read_caption(txt)
        if not cap:
            empty.append(txt.name)
            continue
        caption_count += 1
        words = [w.strip() for w in cap.replace("\n", ",").split(",") if w.strip()]
        total_words += len(words)
        if len(words) < 3:
            short.append(f"{txt.name}: {cap}")
        if len(words) > 40:
            long.append(f"{txt.name}: {len(words)} tags")
        lower = cap.lower()
        if hints and not any(h.lower() in lower for h in hints):
            target_missing.append(f"{txt.name}: {cap[:120]}")
        found_noise = [w for w in noise if w in lower]
        if found_noise:
            noise_hits.append(f"{txt.name}: {', '.join(found_noise)}")

    avg_words = total_words / caption_count if caption_count else 0.0
    if ja:
        lines = [
            "# Caption診断",
            "",
            f"画像数: {len(imgs)}",
            f"captionあり: {caption_count}",
            f"captionなし: {len(missing)}",
            f"空caption: {len(empty)}",
            f"平均タグ数: {avg_words:.1f}",
            f"短すぎるcaption: {len(short)}",
            f"長すぎるcaption: {len(long)}",
            f"学習対象語が見つからない可能性: {len(target_missing)}",
            f"ノイズ語の可能性: {len(noise_hits)}",
        ]
    else:
        lines = [
            "# Caption Diagnostics",
            "",
            f"Images: {len(imgs)}",
            f"Captions found: {caption_count}",
            f"Missing captions: {len(missing)}",
            f"Empty captions: {len(empty)}",
            f"Average tag count: {avg_words:.1f}",
            f"Too short: {len(short)}",
            f"Too long: {len(long)}",
            f"Possibly missing target words: {len(target_missing)}",
            f"Possible noise words: {len(noise_hits)}",
        ]

    def add(title_ja: str, title_en: str, items: list[str]) -> None:
        if items:
            lines.append(f"\n## {title_ja if ja else title_en}")
            lines.extend(f"- {item}" for item in items[:15])
            if len(items) > 15:
                lines.append(f"...他 {len(items) - 15} 件" if ja else f"...and {len(items) - 15} more")

    add("captionなし", "Missing captions", missing)
    add("空caption", "Empty captions", empty)
    add("短すぎるcaption", "Too short", short)
    add("長すぎるcaption", "Too long", long)
    add("学習対象語が見つからない可能性", "Possibly missing target words", target_missing)
    add("ノイズ語の可能性", "Possible noise words", noise_hits)

    if not missing and not empty and not short:
        lines.append("\n次: Configタブへ進んでください。" if ja else "\nNext: Proceed to Config.")
    else:
        lines.append("\n次: captionを確認・修正してから進んでください。" if ja else "\nNext: Review and fix captions before continuing.")
    return "\n".join(lines)

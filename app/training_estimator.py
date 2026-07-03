from __future__ import annotations

from pathlib import Path

from pipeline import image_files


def estimate_training_load(dataset_dir: Path, epochs: int, rank: int, resolution: int, lang: str = "日本語") -> str:
    ja = lang != "English"
    images = len(image_files(dataset_dir))
    if images <= 0:
        return "画像が見つかりません。" if ja else "No images found."

    # This is deliberately a coarse relative score, not a promise of wall-clock time.
    resolution_factor = (resolution / 512) ** 2
    rank_factor = max(rank, 1) / 16
    score = images * max(epochs, 1) * resolution_factor * rank_factor

    if score < 800:
        level_ja, level_en = "軽め", "Light"
        note_ja = "初回テスト向きです。"
        note_en = "Good for an initial test."
    elif score < 2500:
        level_ja, level_en = "標準", "Moderate"
        note_ja = "通常の学習量です。"
        note_en = "Typical training load."
    else:
        level_ja, level_en = "重め", "Heavy"
        note_ja = "時間がかかる可能性があります。Rank/Epoch/Resolutionを下げる選択肢があります。"
        note_en = "May take longer. Consider lowering Rank/Epoch/Resolution."

    if ja:
        return "\n".join([
            "# 学習負荷の目安",
            "",
            f"画像数: {images}",
            f"Epochs: {epochs}",
            f"Rank: {rank}",
            f"Resolution: {resolution}",
            f"負荷目安: {level_ja}",
            note_ja,
            "",
            "注意: これは実測時間ではなく、設定の重さを比較するための目安です。",
        ])
    return "\n".join([
        "# Training Load Estimate",
        "",
        f"Images: {images}",
        f"Epochs: {epochs}",
        f"Rank: {rank}",
        f"Resolution: {resolution}",
        f"Load: {level_en}",
        note_en,
        "",
        "Note: This is not a wall-clock time promise; it is a relative load estimate.",
    ])

from __future__ import annotations

import re


ERROR_PATTERNS: list[tuple[str, str, str]] = [
    (
        "CUDA out of memory",
        "GPUメモリ不足の可能性があります。",
        "解像度、rank、同時処理数を下げてください。PGXでも高解像度・高rankではキャッシュまたは学習でメモリが詰まることがあります。",
    ),
    (
        "out of memory",
        "メモリ不足の可能性があります。",
        "解像度、rank、epochs、キャッシュ条件を見直してください。まずはプリセットのSafe系に戻すのが安全です。",
    ),
    (
        "No such file or directory",
        "ファイルパスが間違っている可能性があります。",
        "設定タブのmusubi-tuner、Z-Image DiT/VAE/Text Encoder、dataset.tomlの場所を確認してください。",
    ),
    (
        "ModuleNotFoundError",
        "Python依存ライブラリが不足しています。",
        "musubi-tuner側のvenvとGUI側のvenvを取り違えていないか確認してください。musubi python pathも確認してください。",
    ),
    (
        "ImportError",
        "Pythonモジュールのimportに失敗しています。",
        "musubi-tunerの環境と、このGUIの環境を取り違えていないか確認してください。",
    ),
    (
        "KeyError",
        "設定ファイルまたはdataset設定に必要なキーがない可能性があります。",
        "dataset.tomlを作り直し、settings.tomlのZ-Image項目が揃っているか確認してください。",
    ),
    (
        "RuntimeError",
        "実行時エラーが発生しています。",
        "直前の数行に本当の原因が出ていることが多いです。ログ末尾を確認してください。",
    ),
    (
        "accelerate",
        "accelerate関連の設定問題の可能性があります。",
        "musubi-tuner環境でaccelerateが使えるか確認してください。GUIのPythonではなくmusubi python path側が重要です。",
    ),
    (
        "dataset_config",
        "dataset.toml関連の問題の可能性があります。",
        "設定生成タブでdataset.tomlを作り直し、画像フォルダとcaptionを確認してください。",
    ),
    (
        "safetensors",
        "モデルファイルの読み込み問題の可能性があります。",
        "Z-Image DiT/VAE/Text Encoderのファイルパス、ファイル形式、破損の有無を確認してください。",
    ),
    (
        "zimage_cache_latents",
        "Latent Cache段階で失敗しています。",
        "dataset.toml、画像ファイル、VAEパスを優先して確認してください。",
    ),
    (
        "zimage_cache_text_encoder_outputs",
        "Text Encoder Cache段階で失敗しています。",
        "Text Encoderパス、caption内容、文字コード、空captionを確認してください。",
    ),
    (
        "zimage_train_network",
        "学習本体で失敗しています。",
        "DiTパス、rank/alpha/lr、キャッシュ出力、出力フォルダ権限を確認してください。",
    ),
]


def extract_recent_error_lines(log_text: str, max_lines: int = 20) -> list[str]:
    keywords = ["error", "exception", "traceback", "failed", "runtimeerror", "modulenotfounderror", "cuda", "zimage", "dataset"]
    lines = log_text.splitlines()
    hits = []
    for line in lines:
        lower = line.lower()
        if any(k in lower for k in keywords):
            hits.append(line)
    return hits[-max_lines:]


def summarize_stage(log_text: str) -> str:
    lower = log_text.lower()
    if "zimage_cache_latents" in lower:
        return "推定段階: Latent Cache"
    if "zimage_cache_text_encoder_outputs" in lower:
        return "推定段階: Text Encoder Cache"
    if "zimage_train_network" in lower:
        return "推定段階: Train"
    return "推定段階: 不明"


def analyze_log(log_text: str) -> str:
    if not log_text.strip():
        return "ログがありません。"

    findings: list[str] = []
    for pattern, title, advice in ERROR_PATTERNS:
        if re.search(re.escape(pattern), log_text, re.IGNORECASE):
            findings.append(f"- **{title}**\n  - {advice}")

    recent = extract_recent_error_lines(log_text)

    if not findings and not recent:
        return "明確な既知エラーパターンは見つかりませんでした。ログ末尾を確認してください。"

    lines = ["# Error Analysis", "", summarize_stage(log_text), ""]
    if findings:
        lines.append("## Possible causes")
        lines.extend(findings)
        lines.append("")
    if recent:
        lines.append("## Recent error lines")
        lines.extend(f"```text\n{line}\n```" for line in recent[-8:])
    lines.append("")
    lines.append("## Next action")
    lines.append("1. まず上の推定段階を確認してください。")
    lines.append("2. Settings / dataset.toml / caption / モデルパスの順に確認してください。")
    lines.append("3. 修正後、Preflight Check → Command Preview → 該当ステップ実行の順にやり直してください。")
    return "\n".join(lines)

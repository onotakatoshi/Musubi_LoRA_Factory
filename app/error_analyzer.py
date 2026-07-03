from __future__ import annotations

import re


ERROR_PATTERNS: list[tuple[str, str, str]] = [
    (
        "CUDA out of memory",
        "GPUメモリ不足の可能性があります。",
        "batch size、解像度、rankを下げるか、block swap / fp8 / offload設定を検討してください。",
    ),
    (
        "No such file or directory",
        "ファイルパスが間違っている可能性があります。",
        "settings.toml の musubi/model path、dataset.toml の場所を確認してください。",
    ),
    (
        "ModuleNotFoundError",
        "Python依存ライブラリが不足しています。",
        "musubi-tuner側のvenvで pip install -r requirements.txt が済んでいるか確認してください。",
    ),
    (
        "ImportError",
        "Pythonモジュールのimportに失敗しています。",
        "musubi-tunerの環境と、このGUIの環境を取り違えていないか確認してください。",
    ),
    (
        "KeyError",
        "設定ファイルまたはdataset設定に必要なキーがない可能性があります。",
        "dataset.toml と settings.toml の内容を確認してください。",
    ),
    (
        "RuntimeError",
        "実行時エラーが発生しています。",
        "直前の数行に本当の原因が出ていることが多いです。ログ末尾を確認してください。",
    ),
    (
        "accelerate",
        "accelerate関連の設定問題の可能性があります。",
        "musubi-tuner環境で accelerate config が必要か確認してください。",
    ),
    (
        "dataset_config",
        "dataset.toml関連の問題の可能性があります。",
        "Configタブでdataset.tomlを作り直し、画像フォルダとcaptionを確認してください。",
    ),
    (
        "safetensors",
        "モデルファイルの読み込み問題の可能性があります。",
        "DiT/VAE/T5のファイルパスとファイル形式を確認してください。",
    ),
]


def extract_recent_error_lines(log_text: str, max_lines: int = 20) -> list[str]:
    keywords = ["error", "exception", "traceback", "failed", "runtimeerror", "modulenotfounderror", "cuda"]
    lines = log_text.splitlines()
    hits = []
    for line in lines:
        lower = line.lower()
        if any(k in lower for k in keywords):
            hits.append(line)
    return hits[-max_lines:]


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

    lines = ["# Error Analysis", ""]
    if findings:
        lines.append("## Possible causes")
        lines.extend(findings)
        lines.append("")
    if recent:
        lines.append("## Recent error lines")
        lines.extend(f"```text\n{line}\n```" for line in recent[-8:])
    return "\n".join(lines)

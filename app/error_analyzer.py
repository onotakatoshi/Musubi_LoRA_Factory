from __future__ import annotations

import re


ERROR_PATTERNS: list[tuple[str, str, str]] = [
    (
        "sm_121 is not compatible with the current PyTorch installation",
        "PyTorchがPGX / GB10のCUDAアーキテクチャに未対応です。",
        "現在のtorch wheelがGB10向けkernelを含んでいません。musubi-tuner側venvのtorchを、CUDA 13系などGB10でCUDA tensorが作れる版へ入れ替えてください。",
    ),
    (
        "no kernel image is available for execution on the device",
        "CUDA kernelがPGX / GB10で実行できません。",
        "VAEやText Encoderの問題ではなく、torchのCUDAビルド不一致が原因です。torch.cuda.get_arch_list() に sm_120 または compute_120 があり、CUDA tensor作成が通る環境へ入れ替えてください。",
    ),
    (
        "No training items found in the dataset",
        "Latent/Text Encoder cacheが未作成、または古い可能性があります。",
        "dataset.tomlを作り直した後は、Trainの前に必ず Latent Cache → Text Encoder Cache を再実行してください。cacheフォルダを消した場合も同じです。",
    ),
    (
        "total batches: 0",
        "学習に使えるcache済みデータが0件です。",
        "画像が見つかっていても、cacheが無いとTrainは開始できません。Latent Cache実行とText Cache実行のログがDONEになっているか確認してください。",
    ),
    (
        "found 0 images",
        "dataset.tomlの画像フォルダを見失っています。",
        "dataset.tomlを作り直してください。image_directory が /home/... で始まる絶対パスになっている必要があります。",
    ),
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
        "コンフィグ生成タブでdataset.tomlを作り直し、画像フォルダとcaptionを確認してください。",
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
    keywords = ["error", "exception", "traceback", "failed", "runtimeerror", "modulenotfounderror", "cuda", "zimage", "dataset", "training items", "total batches", "sm_121", "sm_120", "compute_120", "kernel image"]
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
    if "sm_121 is not compatible" in log_text or "no kernel image is available for execution on the device" in log_text:
        lines.append("1. musubi-tuner側venvのtorchをGB10対応版に入れ替えてください。")
        lines.append("2. torch.cuda.get_arch_list()にsm_120/compute_120があり、CUDA tensor作成が通ることを確認してください。")
        lines.append("3. その後、Latent Cache → Text Encoder Cache → Trainの順に再実行してください。")
    elif "No training items found in the dataset" in log_text or "total batches: 0" in log_text:
        lines.append("1. コンフィグ生成タブでdataset.tomlを作り直してください。")
        lines.append("2. 出力フォルダのcacheを消した場合は、Latent Cache → Text Encoder Cacheを再実行してください。")
        lines.append("3. その後にTrainを実行してください。")
    else:
        lines.append("1. まず上の推定段階を確認してください。")
        lines.append("2. Settings / dataset.toml / caption / モデルパスの順に確認してください。")
        lines.append("3. 修正後、Preflight Check → Command Preview → 該当ステップ実行の順にやり直してください。")
    return "\n".join(lines)

from __future__ import annotations

import re

# Lines that mean the run actually broke. Without one of these the log is treated as
# healthy: the previous version matched bare words like "accelerate", "dataset_config"
# and "safetensors", which appear in every successful command line, so a run that
# trained perfectly was reported as three possible failures.
FAILURE_SIGNALS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^Traceback \(most recent call last\)", re.M),
    re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_.]*(Error|Exception)\s*:", re.M),
    re.compile(r"^\s*assert\b", re.M),
    re.compile(r"COMMAND PATH GUARD FAILED"),
    re.compile(r"\bout of memory\b", re.I),
    re.compile(r"\bKilled\b"),
    re.compile(r"returned non-zero exit status"),
    re.compile(r"CalledProcessError"),
    re.compile(r"^NG:", re.M),
    re.compile(r"===== .*(失敗|FAILED|failed)", re.M),
)

# Noise that looks like a failure but is not.
BENIGN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"Failed to import sageattention"),
    re.compile(r"Trying to import sageattention"),
)

# (regex, title, advice). Matched only after a failure signal is present, and written to
# be specific enough that a healthy log cannot trigger them.
ERROR_PATTERNS: list[tuple[str, str, str]] = [
    (
        r"\.triton[/\\]cache",
        "Triton cacheフォルダの権限問題です。",
        "~/.triton/cache に書き込めていません。アプリは書き込み可能な場所へ自動で退避しますが、CLIから直接実行した場合は `sudo chown -R $USER ~/.triton/cache` で直せます。",
    ),
    (
        r"Permission denied",
        "権限エラーです。",
        "ログに出ているパスの所有者と書き込み権限を確認してください。",
    ),
    (
        r"is on cpu, expected cuda after wait",
        "ブロックスワップが上限値付近で失敗しています。",
        "blocks_to_swap を下げるか、メモリに余裕があれば 0（スワップ無し）にしてください。musubi-tunerは len(blocks)-2 まで許可しますが、その最大値では実際に失敗します。",
    ),
    (
        r"HeaderTooLarge",
        "safetensorsとして読めないファイルを指定しています。",
        "`*.safetensors.index.json` を指定していないか確認してください。分割された重みは先頭ファイル（-00001-of-0000N.safetensors）を指定します。",
    ),
    (
        r"sm_\d+ is not compatible with the current PyTorch installation",
        "PyTorchがこのGPUのCUDAアーキテクチャに未対応です。",
        "musubi-tuner側venvのtorchを、このGPU向けkernelを含む版へ入れ替えてください。",
    ),
    (
        r"no kernel image is available for execution on the device",
        "CUDA kernelがこのGPUで実行できません。",
        "モデルファイルではなくtorchのCUDAビルド不一致が原因です。torch.cuda.get_arch_list() を確認してください。",
    ),
    (
        r"No training items found in the dataset",
        "Latent / Text Encoder cacheが未作成、または古い可能性があります。",
        "dataset.tomlを作り直した後は、学習の前に必ず Latent Cache → Text Cache を再実行してください。",
    ),
    (
        r"total batches: 0",
        "学習に使えるcache済みデータが0件です。",
        "Latent Cache と Text Cache が完了しているか確認してください。",
    ),
    (
        r"found 0 images",
        "dataset.tomlの画像フォルダを見失っています。",
        "image_directory が絶対パスになっているか確認し、コンフィグ生成タブで作り直してください。",
    ),
    (
        r"CUDA out of memory|\bout of memory\b",
        "メモリ不足です。",
        "解像度・rank を下げるか、blocks_to_swap を上げてください。他のGPUプロセス（ComfyUI等）が動いていないかも確認してください。",
    ),
    (
        r"No such file or directory",
        "ファイルパスが間違っている可能性があります。",
        "設定タブのmusubi-tunerパス、選択中モデルのモデルパス、dataset.tomlの場所を確認してください。",
    ),
    (
        r"ModuleNotFoundError",
        "Python依存ライブラリが不足しています。",
        "musubi-tuner側のvenvとGUI側のvenvを取り違えていないか、musubi python path を確認してください。",
    ),
    (
        r"^\s*ImportError\s*:",
        "Pythonモジュールのimportに失敗しています。",
        "musubi-tunerの環境とこのGUIの環境を取り違えていないか確認してください。",
    ),
    (
        r"^\s*KeyError\s*:",
        "設定またはdataset設定に必要なキーがありません。",
        "dataset.tomlを作り直し、settings.tomlの選択中モデルの項目が揃っているか確認してください。",
    ),
    (
        r"unrecognized arguments",
        "musubi-tunerが受け付けないオプションを渡しています。",
        "musubi-tunerを更新したか確認してください。バージョン差でオプション名が変わることがあります。",
    ),
]

# script name -> stage label. Covers every wired model, not just Z-Image.
STAGE_SCRIPTS: tuple[tuple[str, str], ...] = (
    ("cache_text_encoder_outputs", "Text Encoder Cache"),
    ("cache_latents", "Latent Cache"),
    ("cache_pixel", "Latent Cache"),
    ("train_network", "Train"),
)


def _strip_benign(log_text: str) -> str:
    kept = []
    for line in log_text.splitlines():
        if any(p.search(line) for p in BENIGN_PATTERNS):
            continue
        kept.append(line)
    return "\n".join(kept)


def has_failure(log_text: str) -> bool:
    text = _strip_benign(log_text)
    return any(p.search(text) for p in FAILURE_SIGNALS)


def extract_recent_error_lines(log_text: str, max_lines: int = 12) -> list[str]:
    """Lines that are part of an actual failure, not every line mentioning 'cuda'."""
    hits: list[str] = []
    for line in _strip_benign(log_text).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("INFO:", "DEBUG:")):
            continue
        if any(p.search(line) for p in FAILURE_SIGNALS) or stripped.startswith(("File \"", "Traceback")):
            hits.append(line.rstrip())
    return hits[-max_lines:]


def summarize_stage(log_text: str) -> str:
    lower = log_text.lower()
    for marker, label in (("failed text_cache", "Text Encoder Cache"), ("failed latent_cache", "Latent Cache"), ("failed train", "Train")):
        if marker in lower:
            return f"推定段階: {label}"
    # Otherwise use the last script named in the log, so the stage follows whichever
    # model is being trained.
    last_label = ""
    last_pos = -1
    for needle, label in STAGE_SCRIPTS:
        pos = lower.rfind(needle)
        if pos > last_pos:
            last_pos, last_label = pos, label
    return f"推定段階: {last_label}" if last_label else "推定段階: 不明"


def _last_progress_line(log_text: str) -> str:
    for line in reversed(log_text.replace("\r", "\n").splitlines()):
        if "steps:" in line or "epoch " in line:
            return line.strip()
    return ""


def analyze_log(log_text: str) -> str:
    if not log_text.strip():
        return "ログがありません。"

    if not has_failure(log_text):
        lines = ["# Error Analysis", "", "✅ 失敗を示す記録は見つかりませんでした。", ""]
        progress = _last_progress_line(log_text)
        if progress:
            lines.append(f"最後の進捗: {progress}")
            lines.append("")
        lines.append(summarize_stage(log_text))
        lines.append("")
        lines.append("`Failed to import sageattention` のような警告は正常です（代替の実装が使われます）。")
        return "\n".join(lines)

    text = _strip_benign(log_text)
    findings = [
        f"- **{title}**\n  - {advice}"
        for pattern, title, advice in ERROR_PATTERNS
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    ]
    recent = extract_recent_error_lines(log_text)

    lines = ["# Error Analysis", "", "❌ 失敗が記録されています。", "", summarize_stage(log_text), ""]
    if findings:
        lines.append("## Possible causes")
        lines.extend(findings)
        lines.append("")
    else:
        lines.append("既知のパターンには一致しませんでした。下の行を確認してください。")
        lines.append("")
    if recent:
        lines.append("## Error lines")
        lines.extend(f"```text\n{line}\n```" for line in recent[-8:])
        lines.append("")
    lines.append("## Next action")
    if re.search(r"is on cpu, expected cuda after wait", text):
        lines.append("1. blocks_to_swap を下げてください（メモリに余裕があれば 0）。")
        lines.append("2. その後、学習を再実行してください。cacheは作り直し不要です。")
    elif re.search(r"HeaderTooLarge", text):
        lines.append("1. 設定タブのモデルパスに `*.safetensors.index.json` が無いか確認してください。")
        lines.append("2. 分割ファイルは先頭（-00001-of-0000N.safetensors）を指定してください。")
    elif re.search(r"No training items found|total batches: 0", text):
        lines.append("1. コンフィグ生成タブで dataset.toml を作り直してください。")
        lines.append("2. Latent Cache → Text Cache を再実行してから学習してください。")
    elif re.search(r"out of memory", text, re.IGNORECASE):
        lines.append("1. 解像度か rank を下げてください。")
        lines.append("2. 他のGPUプロセス（ComfyUI等）を止めてください。")
        lines.append("3. それでも足りなければ blocks_to_swap を上げてください。")
    else:
        lines.append("1. 上の Error lines の最初の行を確認してください。本当の原因はそこにあることが多いです。")
        lines.append("2. 推定段階に対応する設定（モデルパス / dataset.toml / caption）を確認してください。")
        lines.append("3. 修正後、該当ステップを再実行してください。")
    return "\n".join(lines)

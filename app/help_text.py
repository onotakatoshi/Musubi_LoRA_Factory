from __future__ import annotations

HELP = {
    "dataset_dir": "学習用画像を入れたフォルダです。画像と同じ名前の .txt がcaptionです。例: sample.png / sample.txt",
    "lora_type": "何を学習したいかを指定します。eyeなら目に関係ない髪・服・背景などをcaptionから削る方向にします。",
    "caption_mode": "caption作成方法です。joycaption_llmはJoyCaptionの結果をLLMで整理します。manualは自分でtxtを書く前提です。",
    "output_dir": "dataset.toml、cache、学習済みLoRAを置く出力フォルダです。実験ごとに別フォルダ推奨です。",
    "resolution": "学習解像度です。最初は512推奨。画像が512x512中心なら512で始めるのが安全です。",
    "target_model": "どのモデル向けLoRAを作るかです。現在はZ-Imageを優先しています。",
    "task": "モデルごとの学習プロファイルです。Z-Imageではz-imageを選びます。Wan用の項目は後続対応です。",
    "rank": "LoRAの表現力です。大きいほど覚えられますが重く、過学習しやすくなります。最初は16推奨です。",
    "alpha": "LoRAの効きのスケールです。最初はrankと同じ値、つまり16/16が分かりやすいです。",
    "epochs": "データセットを何周学習するかです。最初は10程度。効きすぎるなら下げます。",
    "lr": "学習率です。大きすぎると壊れ、小さすぎると覚えません。最初は0.00005推奨です。",
    "output_name": "保存されるLoRA名です。例: eye_lora_zimage。拡張子はmusubi-tuner側が付けます。",
    "preflight": "実行前チェックです。settings.toml、dataset.toml、モデルパスが揃っているか確認します。",
    "preview": "実際に実行するコマンドを表示します。Runボタンを押す前に必ず確認します。",
    "latent_cache": "画像をVAEで潜在表現に変換してcacheします。最初に実行します。",
    "text_cache": "captionをText Encoderで変換してcacheします。Latent Cacheの次に実行します。",
    "train": "cache済みデータを使ってLoRAを学習します。最後に実行します。",
    "export": "完成したLoRAをComfyUIのlorasフォルダにコピーします。",
}


def help_markdown(topic: str) -> str:
    if topic == "all":
        lines = ["# Help", ""]
        for key, text in HELP.items():
            lines.append(f"## {key}\n{text}\n")
        return "\n".join(lines)
    return f"## {topic}\n{HELP.get(topic, '説明がまだ登録されていません。')}"

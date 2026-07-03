# Musubi LoRA Factory

PGX向けのmusubi-tuner用ローカルGUIです。

目的:
- データセット選択
- JoyCaption/LLM整形用のキャプション生成パイプライン
- caption一覧編集
- dataset.toml自動生成
- musubi-tunerのcache/trainコマンドPreview
- Preflight Check
- musubi-tunerコマンド実行
- リアルタイムログ表示とログ保存
- GPU状態表示
- 完成LoRAをComfyUIへコピー

> まだMVPです。最初はWan2.2向けプロファイルを優先しています。

## PGXでの起動

```bash
git clone https://github.com/onotakatoshi/Musubi_LoRA_Factory.git
cd Musubi_LoRA_Factory
chmod +x scripts/setup.sh scripts/start.sh
./scripts/setup.sh
```

`configs/settings.toml` をPGX環境に合わせて編集します。

その後、起動します。

```bash
./scripts/start.sh
```

ブラウザで表示されたURLを開きます。

## 手動起動

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp configs/settings.example.toml configs/settings.toml
python app/main.py
```

## 基本フロー

1. `Dataset` で画像フォルダを指定
2. `Check Dataset` で画像数・サイズ・caption有無を確認
3. `Generate Captions` で `.txt` captionを生成
4. `Caption Editor` でcaptionを確認・修正
5. `Config` で `dataset.toml` を作成
6. `Train` で `0. Preflight Check`
7. `Preview Commands` で実行内容を確認
8. `Run 1: Latent Cache`
9. `Run 2: Text Cache`
10. `Run 3: Train`
11. `Export` で完成LoRAをComfyUIへコピー

## Caption

`joycaption_command` を設定するとJoyCaptionを外部コマンドとして呼び出します。

```toml
joycaption_command = "python /opt/JoyCaption/caption.py --image {image}"
```

LLMはOpenAI互換APIを想定しています。

```toml
llm_endpoint = "http://localhost:8000/v1/chat/completions"
llm_model = "qwen-caption-helper"
```

## Wan2.2 paths

Wan2.2では、少なくともVAE、T5、DiTのパスが必要です。

```toml
[model_paths]
wan_vae = "/home/ono/models/wan/Wan2.1_VAE.pth"
wan_t5 = "/home/ono/models/wan/models_t5_umt5-xxl-enc-bf16.pth"
wan_dit = "/home/ono/models/wan/wan2.2_low_noise.safetensors"
wan_dit_high_noise = "/home/ono/models/wan/wan2.2_high_noise.safetensors"
```

最初に `0. Preflight Check` を押すと、不足しているパスが表示されます。

## Logs

実行ログは `logs/` に保存されます。

GUI上部の `Recent Logs` から直近ログを確認できます。

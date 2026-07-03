# Musubi LoRA Factory

PGX向けのmusubi-tuner用ローカルGUIです。

現在の優先ターゲットは **Z-Image / Z-Image-Turbo運用** です。

Z-Imageで最初に試す場合は、まず [PGX Z-Image setup notes](docs/pgx_zimage_setup.md) を見てください。

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

> まだMVPです。まずZ-Image向けプロファイルを優先し、その後Wan2.2/FLUXへ広げます。

## PGXでの起動

```bash
git clone https://github.com/onotakatoshi/Musubi_LoRA_Factory.git
cd Musubi_LoRA_Factory
chmod +x scripts/setup.sh scripts/start.sh scripts/check.sh
./scripts/setup.sh
./scripts/check.sh
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
python -m py_compile app/*.py
python app/smoke_test.py
python app/main.py
```

## 基本フロー

1. `Dataset` で画像フォルダを指定
2. `Check Dataset` で画像数・サイズ・caption有無を確認
3. `Generate Captions` で `.txt` captionを生成
4. `Caption Editor` でcaptionを確認・修正
5. `Config` で `dataset.toml` を作成
6. `Train` で Target model が `z-image` になっていることを確認
7. `0. Preflight Check`
8. `Preview Commands` で実行内容を確認
9. `Run 1: Latent Cache`
10. `Run 2: Text Cache`
11. `Run 3: Train`
12. `Export` で完成LoRAをComfyUIへコピー

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

## Z-Image paths

Z-Imageでは、少なくともVAE、Text Encoder、DiTのパスが必要です。

```toml
[model_paths]
zimage_dit = "/home/ono/models/z-image/z_image_base_or_deturbo.safetensors"
zimage_vae = "/home/ono/models/z-image/ae.safetensors"
zimage_text_encoder = "/home/ono/models/z-image/qwen3_text_encoder_00001-of-00002.safetensors"
zimage_base_weights = ""
```

`zimage_base_weights` は任意です。

注意:
- Turbo系そのものを直接学習するより、BaseまたはDe-Turbo系DiTを学習対象にする想定です。
- 作成したLoRAをZ-Image-Turbo生成ワークフローでテストする運用を優先します。

## Wan2.2 paths

Wan2.2も後続対応として残しています。

```toml
[model_paths]
wan_vae = "/home/ono/models/wan/Wan2.1_VAE.pth"
wan_t5 = "/home/ono/models/wan/models_t5_umt5-xxl-enc-bf16.pth"
wan_dit = "/home/ono/models/wan/wan2.2_low_noise.safetensors"
wan_dit_high_noise = "/home/ono/models/wan/wan2.2_high_noise.safetensors"
```

## Logs

実行ログは `logs/` に保存されます。

GUI上部の `Recent Logs` から直近ログを確認できます。

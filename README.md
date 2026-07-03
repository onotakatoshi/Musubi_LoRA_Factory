# Musubi LoRA Factory

PGX向けのmusubi-tuner用ローカルデスクトップGUIです。

現在の優先ターゲットは **Z-Image / Z-Image-Turbo運用** です。

Z-Imageで最初に試す場合は、まず [PGX Z-Image setup notes](docs/pgx_zimage_setup.md) を見てください。

目的:
- データセット選択
- caption診断
- caption一覧編集
- caption一括置換 / 一括削除
- dataset.toml自動生成
- musubi-tunerのcache/trainコマンドPreview
- Preflight Check
- musubi-tunerコマンド実行
- リアルタイムログ表示
- GPU状態表示
- 完成LoRAをComfyUIへコピー

> 初期版はPySide6の普通のデスクトップアプリとして作ります。ブラウザ/localhost前提ではありません。

## PGXでの起動

```bash
git clone https://github.com/onotakatoshi/Musubi_LoRA_Factory.git
cd Musubi_LoRA_Factory
chmod +x scripts/setup.sh scripts/start.sh scripts/check.sh scripts/create_desktop_launcher.sh
./scripts/setup.sh
./scripts/check.sh
```

初回設定はアプリの `設定` タブから行います。

その後、起動します。

```bash
./scripts/start.sh
```

PySide6のデスクトップウィンドウが開きます。

## アイコンから起動

Linuxデスクトップ環境では、デスクトップアイコンを作れます。

```bash
./scripts/create_desktop_launcher.sh
```

作成されるもの:

- `~/Desktop/Musubi LoRA Factory.desktop`
- `~/.local/share/applications/Musubi LoRA Factory.desktop`

GNOMEなどでは、初回だけデスクトップアイコンを右クリックして **Allow Launching** を選ぶ必要があります。

以後は、アイコンをダブルクリックして起動できます。

## 手動起動

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp configs/settings.example.toml configs/settings.toml
python -m py_compile app/*.py
python app/desktop_static_check.py
python app/smoke_test.py
python app/desktop_main.py
```

## 基本フロー

1. `設定` で musubi-tuner / Z-Image / ComfyUI のパスを設定
2. `システム` で Environment Check / GPU Status を確認
3. `データセット` で画像フォルダを指定
4. `データセット確認` で画像数・サイズ・caption有無・重複を確認
5. `Caption診断` でcaptionの不足やノイズ語を確認
6. `Caption編集` でcaptionを一覧編集、一括置換、一括削除
7. `設定生成` で `dataset.toml` を作成
8. `学習` で Target model が `z-image` になっていることを確認
9. `0. 事前チェック`
10. `コマンド確認` で実行内容を確認
11. `1. Latent Cache実行`
12. `2. Text Cache実行`
13. `3. 学習実行`
14. `書き出し` で完成LoRAをComfyUIへコピー

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

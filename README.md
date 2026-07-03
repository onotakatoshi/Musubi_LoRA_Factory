# Musubi LoRA Factory

PGX向けのmusubi-tuner用ローカルデスクトップGUIです。

現在の優先ターゲットは **Z-Image / Z-Image-Turbo運用** です。

Z-Imageで最初に試す場合は、まず [PGX Z-Image setup notes](docs/pgx_zimage_setup.md) を見てください。

目的:
- データセット選択
- caption確認
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

`configs/settings.toml` をPGX環境に合わせて編集します。

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
python app/smoke_test.py
python app/desktop_main.py
```

## 基本フロー

1. `System` で Environment Check / GPU Status を確認
2. `Dataset` で画像フォルダを指定
3. `Check Dataset` で画像数・サイズ・caption有無を確認
4. `Config` で `dataset.toml` を作成
5. `Train` で Target model が `z-image` になっていることを確認
6. `0. Preflight Check`
7. `Preview Commands` で実行内容を確認
8. `Run 1: Latent Cache`
9. `Run 2: Text Cache`
10. `Run 3: Train`
11. `Export` で完成LoRAをComfyUIへコピー

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

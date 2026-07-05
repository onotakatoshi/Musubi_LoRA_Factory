# Musubi LoRA Factory

PGX向けのmusubi-tuner用ローカルデスクトップGUIです。

**現在は Z-Image / Z-Image-Turbo と Wan2.2 のLoRA作成に対応を進めています。**

最初の安定対象は Z-Image / Z-Image-Turbo です。Wan2.2 は初期対応として t2v-A14B プロファイル、VAE、T5、low-noise/high-noise DiT のパス指定、コマンド生成、Preflight Check に対応します。

FLUX、SDXL、その他モデルへの対応は、Z-Image / Wan2.2 の実用確認後に追加します。

Z-Imageで最初に試す場合は、まず [PGX Z-Image setup notes](docs/pgx_zimage_setup.md) を見てください。

PGXでβ確認する手順は [PGX Beta Runbook](docs/pgx_beta_runbook.md) にまとめています。

Ver 1.0の合格条件は [Ver 1.0 Acceptance Checklist](docs/v1_acceptance_checklist.md) にまとめています。

目的:
- Z-Image / Z-Image-Turbo 用LoRA作成
- Wan2.2 用LoRA作成
- データセット選択
- キャプション診断
- キャプション一覧編集
- キャプション一括置換 / 一括削除
- 画像プレビューを見ながらキャプション最終確認
- dataset.toml自動生成
- musubi-tuner cache/trainコマンドPreview
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
chmod +x scripts/setup.sh scripts/start.sh scripts/check.sh scripts/update.sh scripts/create_desktop_launcher.sh
./scripts/setup.sh
./scripts/check.sh
```

初回設定はアプリの `設定` タブから行います。

その後、起動します。

```bash
./scripts/start.sh
```

PySide6のデスクトップウィンドウが開きます。

## 更新

```bash
./scripts/update.sh
```

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

1. `設定` で musubi-tuner / Z-Image / Wan2.2 / ComfyUI のパスを設定
2. `システム` で Environment Check / GPU Status を確認
3. `データセット` で画像フォルダを指定
4. `データセット確認` で画像数・サイズ・キャプション有無・重複を確認
5. `キャプション診断` でキャプションの不足やノイズ語を確認
6. `キャプション編集` でキャプションを一覧編集、一括置換、一括削除
7. `画像プレビュー` で画像を見ながらキャプションを最終確認
8. `コンフィグ生成` で `dataset.toml` を作成
9. `学習` で Target model を選択
10. `0. 事前チェック`
11. `コマンド確認` で実行内容を確認
12. `1. Latent Cache`
13. `2. Text Cache`
14. `3. 学習実行`
15. `書き出し` で完成LoRAをComfyUIへコピー
16. ComfyUIの対応ワークフローでLoRAを確認

## Model paths

Z-Imageでは、少なくともVAE、Text Encoder、DiTのパスが必要です。

```toml
[model_paths]
zimage_dit = "../models/z-image/Tongyi-MAI/Z-Image/transformer/diffusion_pytorch_model-00001-of-00002.safetensors"
zimage_vae = "../models/z-image/Tongyi-MAI/Z-Image/vae/diffusion_pytorch_model.safetensors"
zimage_text_encoder = "../models/z-image/Tongyi-MAI/Z-Image/text_encoder/model-00001-of-00003.safetensors"
zimage_base_weights = ""
```

Wan2.2では、VAE、T5、low-noise DiTが必要です。high-noise DiTは設定されている場合に使います。

```toml
[model_paths]
wan_vae = "../models/wan/Wan2.1_VAE.pth"
wan_t5 = "../models/wan/models_t5_umt5-xxl-enc-bf16.pth"
wan_dit = "../models/wan/wan2.2_low_noise.safetensors"
wan_dit_high_noise = "../models/wan/wan2.2_high_noise.safetensors"
```

注意:
- Z-Imageでは、Turbo系そのものを直接学習するより、BaseまたはDe-Turbo系DiTを学習対象にする想定です。
- Wan2.2初期実装では `t2v-A14B` を対象にします。
- 作成したLoRAは、対応するComfyUIワークフローでテストしてください。

## Out of scope for Ver 1.0

以下はVer 1.0では対象外です。

- FLUX LoRA
- SDXL LoRA
- AIアシスタント
- タグヒートマップ
- 学習履歴DB
- 高度な自動修正

これらは、Z-Image / Wan2.2で「ちゃんと使えるLoRA」が作れることを確認したあとに追加します。

# Musubi LoRA Factory

PGX向けのmusubi-tuner用ローカルデスクトップGUIです。

**現在は Z-Image / Z-Image-Turbo と Wan2.2 のLoRA作成に対応を進めています。**

最初の安定対象は Z-Image / Z-Image-Turbo です。Wan2.2 は初期対応として t2v-A14B プロファイル、VAE、T5、low-noise/high-noise DiT のパス指定、コマンド生成、Preflight Check に対応します。

FLUX、SDXL、その他モデルへの対応は、Z-Image / Wan2.2 の実用確認後に追加します。

Z-Imageで最初に試す場合は、まず [PGX Z-Image setup notes](docs/pgx_zimage_setup.md) を見てください。

PGXでβ確認する手順は [PGX Beta Runbook](docs/pgx_beta_runbook.md) にまとめています。

Ver 1.0の合格条件は [Ver 1.0 Acceptance Checklist](docs/v1_acceptance_checklist.md) にまとめています。

新しいTarget modelを追加するときの注意点は [Model Integration Checklist](docs/model_integration_checklist.md) にまとめています。

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
cd ~/Musubi_LoRA_Factory
bash ./scripts/start.sh
```

## 基本の流れ

1. `設定` タブで `musubi-tuner / Z-Image / Wan2.2 / ComfyUI` のパスを設定
2. `System` タブで実行環境チェック
3. `Dataset` タブで画像フォルダ、学習対象、出力先を指定
4. `Caption編集` タブでcaptionを確認・編集
5. `画像プレビュー` タブで画像とcaptionを最終確認
6. `Config` タブで `dataset.toml` を生成
7. `学習` タブでTarget modelを選び、Preflight Check後にcache/trainを実行
8. `Export` タブで完成LoRAをComfyUIへコピー

## 設定ファイル

初回起動前に例をコピーできます。

```bash
cp configs/settings.example.toml configs/settings.toml
```

主な項目:

```toml
[musubi]
repo_path = "../musubi-tuner"
python_path = "../musubi-tuner/.venv/bin/python"

[paths]
datasets_dir = "datasets/lora"
outputs_dir = "outputs/lora"
comfyui_loras_dir = "../ComfyUI/models/loras"

[model_paths]
zimage_dit = "../models/z-image/Tongyi-MAI/Z-Image/transformer/diffusion_pytorch_model-00001-of-00002.safetensors"
zimage_vae = "../models/z-image/Tongyi-MAI/Z-Image/vae/diffusion_pytorch_model.safetensors"
zimage_text_encoder = "../models/z-image/Tongyi-MAI/Z-Image/text_encoder/model-00001-of-00003.safetensors"
zimage_base_weights = ""
wan_vae = "../models/wan/Wan2.2-T2V-A14B/Wan2.1_VAE.pth"
wan_t5 = "../models/wan/Wan2.2-T2V-A14B/models_t5_umt5-xxl-enc-bf16.pth"
wan_dit = "../models/wan/Wan2.2-T2V-A14B/low_noise_model/diffusion_pytorch_model.safetensors.index.json"
wan_dit_high_noise = "../models/wan/Wan2.2-T2V-A14B/high_noise_model/diffusion_pytorch_model.safetensors.index.json"
```

GUIの `設定` タブからBrowseで指定するのが安全です。

## 開発方針

このGUIは、最初にZ-Image / Z-Image-Turbo LoRA作成を安定させることを優先します。

## 現在できること

- 設定チェック
- Dataset検査
- Caption診断
- Caption一覧編集
- 画像プレビュー
- dataset.toml生成
- Training Review
- Preflight Check
- musubi-tunerコマンドPreview
- musubi-tunerコマンド実行
- ログ解析
- GPU状態表示
- LoRA Export検証
- ComfyUIへのコピー

## 現時点で対象外

- FLUX / HunyuanVideo / SDXLなどの本格対応
- マルチGPU分散
- クラウド実行

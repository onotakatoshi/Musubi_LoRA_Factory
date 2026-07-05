# Musubi LoRA Factory

PGX向けのmusubi-tuner用ローカルデスクトップGUIです。

**Musubi TunerでLoRA作成スクリプトが用意されている主要Target modelを、設定画面の選択肢として追加しています。**

現在、学習コマンド生成まで実装済みなのは Z-Image / Z-Image-Turbo、Wan2.2 T2V-A14B、Wan2.2 I2V-A14B です。Wan2.2 TI2V-5B とその他のTarget modelは、Settingsのモデル別パス管理・設定確認・保存後ログ・musubiスクリプト確認までを先に追加し、学習コマンドテンプレートは検証フェーズで順次有効化します。

追加対象:

- Z-Image / Z-Image-Turbo
- Wan2.2 T2V-A14B
- Wan2.2 I2V-A14B
- Wan2.2 TI2V-5B
- Wan2.1
- Wan2.1/2.2 Single Frame
- HunyuanVideo
- HunyuanVideo 1.5
- FramePack
- FramePack Single Frame
- FLUX.1 Kontext
- FLUX.2 dev
- FLUX.2 klein
- Qwen-Image
- HiDream-O1-Image
- Kandinsky 5
- Ideogram4
- Krea 2

Z-Imageで最初に試す場合は、まず [PGX Z-Image setup notes](docs/pgx_zimage_setup.md) を見てください。

PGXでβ確認する手順は [PGX Beta Runbook](docs/pgx_beta_runbook.md) にまとめています。

Ver 1.0の合格条件は [Ver 1.0 Acceptance Checklist](docs/v1_acceptance_checklist.md) にまとめています。

新しいTarget modelを追加するときの注意点は [Model Integration Checklist](docs/model_integration_checklist.md) にまとめています。

目的:
- Z-Image / Z-Image-Turbo 用LoRA作成
- Wan2.2 T2V-A14B 用LoRA作成
- Wan2.2 I2V-A14B 用LoRA作成
- Musubi Tuner対応Target modelの設定管理
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
chmod +x scripts/setup.sh scripts/start.sh scripts/check.sh scripts/update.sh scripts/create_desktop_launcher.sh scripts/download_model_assets.sh
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

## モデルファイルの一括ダウンロード

Hugging Faceから必要なモデルファイルをまとめて取得できます。

Wan2.2 T2V / I2V / TI2V をまとめて取得する場合:

```bash
cd ~/Musubi_LoRA_Factory
git pull --ff-only
bash ./scripts/download_model_assets.sh wan22-all
```

Z-Image + Wan2.2 T2V + Wan2.2 I2V の基本セット:

```bash
bash ./scripts/download_model_assets.sh core
```

スクリプトに登録済みの既知モデルをまとめて取得する場合:

```bash
bash ./scripts/download_model_assets.sh all-known
```

保存先を変える場合:

```bash
bash ./scripts/download_model_assets.sh wan22-all --models-dir /mnt/models
```

事前確認だけ行う場合:

```bash
bash ./scripts/download_model_assets.sh wan22-all --dry-run
```

ゲート付きモデルで失敗する場合は、先にHugging Faceでライセンス承認し、PGX上でログインします。

```bash
hf auth login
```

ログは `logs/model_downloads/` に保存されます。

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

1. `設定` タブで `musubi-tuner / Target model / ComfyUI` のパスを設定
2. `System` タブで実行環境チェック
3. `Dataset` タブで画像フォルダ、学習対象、出力先を指定
4. `Caption編集` タブでcaptionを確認・編集
5. `画像プレビュー` タブで画像とcaptionを最終確認
6. `Config` タブで `dataset.toml` を生成
7. `学習` タブでTarget modelを確認し、Preflight Check後にcache/trainを実行
8. `Export` タブで完成LoRAをComfyUIへコピー

## 設定ファイル

初回起動前に例をコピーできます。

```bash
cp configs/settings.example.toml configs/settings.toml
```

GUIの `設定` タブからBrowseで指定するのが安全です。

## 開発方針

このGUIは、最初にZ-Image / Z-Image-Turbo LoRA作成を安定させ、次にWan2.2、その他Musubi Tuner対応モデルへ広げます。

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

- Wan2.2 TI2V-5Bおよび未検証Target modelの学習コマンド実行
- マルチGPU分散
- クラウド実行

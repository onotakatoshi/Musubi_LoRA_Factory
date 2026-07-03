# Musubi LoRA Factory

PGX向けのmusubi-tuner用ローカルデスクトップGUIです。

**Ver 1.0 は Z-Image / Z-Image-Turbo 用LoRA作成に限定します。**

Wan2.2、FLUX、SDXL、その他モデルへの対応は、Z-Image-Turboで実用的なLoRA生成が確認できたあとに追加します。

Z-Imageで最初に試す場合は、まず [PGX Z-Image setup notes](docs/pgx_zimage_setup.md) を見てください。

Ver 1.0の合格条件は [Ver 1.0 Acceptance Checklist](docs/v1_acceptance_checklist.md) にまとめています。

目的:
- Z-Image / Z-Image-Turbo 用LoRA作成
- データセット選択
- caption診断
- caption一覧編集
- caption一括置換 / 一括削除
- 画像プレビューを見ながらcaption最終確認
- dataset.toml自動生成
- Z-Image用musubi-tuner cache/trainコマンドPreview
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

1. `設定` で musubi-tuner / Z-Image / ComfyUI のパスを設定
2. `システム` で Environment Check / GPU Status を確認
3. `データセット` で画像フォルダを指定
4. `データセット確認` で画像数・サイズ・caption有無・重複を確認
5. `Caption診断` でcaptionの不足やノイズ語を確認
6. `Caption編集` でcaptionを一覧編集、一括置換、一括削除
7. `画像プレビュー` で画像を見ながらcaptionを最終確認
8. `設定生成` で `dataset.toml` を作成
9. `学習` で Target model が `z-image` になっていることを確認
10. `Preset適用`
11. `学習前レビュー`
12. `0. 事前チェック`
13. `コマンド確認` で実行内容を確認
14. `1. Latent Cache実行`
15. `2. Text Cache実行`
16. `3. 学習実行`
17. `書き出し` で完成LoRAをComfyUIへコピー
18. ComfyUIのZ-Image-TurboワークフローでLoRAを確認

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

## Out of scope for Ver 1.0

以下はVer 1.0では対象外です。

- Wan2.2 LoRA
- FLUX LoRA
- SDXL LoRA
- AIアシスタント
- タグヒートマップ
- 学習履歴DB
- 高度な自動修正

これらは、Z-Image-Turboで「ちゃんと使えるLoRA」が作れることを確認したあとに追加します。

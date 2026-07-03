# PGX Beta Runbook

PGXでMusubi LoRA Factory Ver 1.0 betaを確認するための最短手順です。

## 1. Install / Update

初回:

```bash
git clone https://github.com/onotakatoshi/Musubi_LoRA_Factory.git
cd Musubi_LoRA_Factory
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/check.sh
./scripts/create_desktop_launcher.sh
```

更新時:

```bash
cd Musubi_LoRA_Factory
./scripts/update.sh
```

## 2. Launch

```bash
./scripts/start.sh
```

またはデスクトップアイコンをダブルクリックします。

設定ファイルがない場合は example から自動作成されます。仮想環境がない場合は、起動時に setup が実行されます。

## 3. Pre-check from terminal

PGXで試す前に、ターミナルから以下を実行すると問題箇所を確認できます。

```bash
./scripts/check.sh
```

チェックは以下の順番で実行されます。

1. PySide6 import
2. Python syntax
3. Startup structure
4. Desktop static check
5. Command preview validation
6. Smoke test
7. Environment check

## 4. Settings tab

設定タブで以下を指定します。

- musubi-tuner repo
- musubi python
- datasets dir
- outputs dir
- ComfyUI loras dir
- Z-Image DiT
- Z-Image VAE
- Z-Image text encoder

その後、以下を押します。

1. `設定を確認`
2. `設定を保存`
3. `環境チェック`

## 5. Dataset tab

1. Dataset folderを選択
2. `データセット確認`
3. `Caption診断`

caption不足や重複があれば直します。

## 6. Caption編集 tab

1. `Captionを読み込み`
2. 必要なら一括置換 / 語句削除
3. `Captionを保存`

## 7. 画像プレビュー tab

1. `画像を読み込み`
2. 画像を見ながらcaptionを確認
3. 必要ならcaptionを修正
4. `現在のCaptionを保存`

## 8. 設定生成 tab

1. Output folderを確認
2. Resolutionを確認
3. `dataset.tomlを作成`

## 9. 学習 tab

1. Target modelが `Z-Image / Z-Image-Turbo` であることを確認
2. `Preset適用`
3. `学習前レビュー`
4. `0. 事前チェック`
5. `コマンド確認`
6. `1. Latent Cache実行`
7. `2. Text Cache実行`
8. `3. 学習実行`

ログにERRORが出た場合は `ログ解析` を押します。

## 10. 書き出し tab

1. 完成したLoRA `.safetensors` を選択
2. `ComfyUIへコピー`
3. ComfyUIのZ-Image-TurboワークフローでLoRAを読み込み、生成確認

## Beta success condition

以下が成功すれば、Z-Image Ver 1.0 betaの実機確認OKです。

```text
起動
→ 設定保存
→ dataset確認
→ caption確認/編集
→ dataset.toml生成
→ latent cache
→ text cache
→ train
→ LoRA出力
→ ComfyUIへコピー
→ Z-Image-Turboで生成確認
```

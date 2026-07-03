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
./scripts/check_beta.sh
./scripts/create_desktop_launcher.sh
```

更新時:

```bash
cd Musubi_LoRA_Factory
./scripts/update.sh
./scripts/check_beta.sh
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
./scripts/check_beta.sh
```

`check.sh` は基本検査、`check_beta.sh` はβ版として必要なランチャー・プロジェクト保存・コマンドPreview・実行直前ガード・Export検証・β状態の追加検査です。

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

または `全部実行` で Latent Cache → Text Cache → Train を連続実行します。

実行直前には Command Path Guard が入り、dataset.toml / model file / musubi repo / musubi python / zimage script が見つからなければ実行を止めます。

実行ログは出力フォルダ配下の `logs/` にも保存されます。ログにERRORが出た場合は `ログ解析` を押します。

## 10. LoRA output check

学習後、必要に応じてターミナルから出力LoRAを確認できます。

```bash
source .venv/bin/activate
python app/find_lora_output.py /path/to/output_dir --name eye_lora_zimage
```

見つかった `.safetensors` は、学習完了時に自動で書き出しタブのLoRAパスへ入ります。自動検出できない場合は手動で選択します。

## 11. 書き出し tab

1. 完成したLoRA `.safetensors` を選択
2. `コピー前チェック`
3. `Result: OK` を確認
4. `ComfyUIへコピー`
5. ComfyUIのZ-Image-TurboワークフローでLoRAを読み込み、生成確認

`コピー前チェック` は、LoRAファイルの存在、`.safetensors` 拡張子、ComfyUI LoRAフォルダ、上書き有無を確認します。NGの場合はコピーしません。

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
→ コピー前チェック
→ ComfyUIへコピー
→ Z-Image-Turboで生成確認
```

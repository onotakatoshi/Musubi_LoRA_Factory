# Model Expansion Checklist

Z-Image / Z-Image-Turboの実機検証が完了したあと、musubi-tunerが対応しているLoRAターゲットを順次追加するためのチェックリストです。

## Rule

モデル追加は、既存UIを作り直さずに行います。

追加単位は以下です。

1. Model profile
2. Model adapter
3. Settings fields
4. Command builder
5. Presets/help text
6. Acceptance test

## 1. Add or enable model profile

`app/model_registry.py` にプロファイルを追加、または `enabled_in_v1` 相当の有効化フラグを切り替えます。

必要項目:

- `id`
- `display_name`
- `task`
- `enabled_in_v1` / future enable flag
- `description_ja`
- `description_en`

## 2. Add model adapter

`app/model_adapters.py` にadapterを追加します。

adapterが持つ責務:

- 必須設定キー
- 任意設定キー
- モデルパス検証
- musubi-tunerコマンド生成

## 3. Add settings UI fields

設定タブにモデル固有パスを追加します。

ただし、UIの骨格は変えません。

- 既存のSettings tabにモデルプロファイル別セクションを追加
- 未選択モデルの設定は折りたたみ、または将来タブ化
- `settings.toml` にはモデルごとのキーを保持

## 4. Add command preview support

`command_preview.py` 自体は大きく変更せず、adapter側で対応します。

追加後の確認:

```bash
python app/command_preview_test.py
python app/smoke_test.py
```

## 5. Add presets

`training_presets.py` をモデルプロファイル対応に拡張します。

初期状態では、モデルごとに安全寄りのプリセットだけを有効にします。

## 6. Add help text

各パラメータの `?` に、モデル別の説明を追加します。

最低限必要な説明:

- 何のための値か
- 推奨デフォルト
- 上げるとどうなるか
- 下げるとどうなるか
- 初回に触るべきか

## 7. Add acceptance checklist

モデルごとに実機確認項目を作ります。

必須:

```text
settings
→ dataset
→ caption check/edit
→ dataset.toml
→ latent/text cache if required
→ train
→ LoRA output
→ ComfyUI generation test
```

## 8. Do not mark as supported before generation test

コマンド生成だけ通っても「対応済み」にしません。

実際にLoRAを出力し、ComfyUI側で生成に反映できた時点で対応済みにします。

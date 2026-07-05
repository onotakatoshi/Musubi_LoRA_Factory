# Model Integration Checklist

このメモは、Wan2.2追加時に発生したUI・設定・ログの不整合を再発させないためのチェックリストです。
新しいTarget modelを追加するときは、実装完了扱いにする前に、必ず以下を確認してください。

## 1. Target modelはSettingsを起点にする

- `Settings`タブにTarget modelを表示する。
- Target modelを切り替えた瞬間に、モデル別設定欄を切り替える。
- Target modelを切り替えた瞬間に、`5. 学習`タブ側のTarget modelも同期する。
- 同期時にTaskも更新する。
- 保存後に再起動しても、保存されたTarget modelから始まることを確認する。

## 2. モデル別設定欄は「必要なものだけ」表示する

- Z-Image選択時にWan系の項目を出さない。
- Wan2.2選択時にZ-Image系の項目を出さない。
- モデルを増やしても縦に欄を積み上げない。
- Settingsは、原則として「左: 共通設定 / 右: モデル別設定」の2カラムを維持する。
- ウインドウが下に伸びて画面外にはみ出さないことを確認する。

## 3. 説明文とヘルプは選択モデルに連動させる

- Settings上部の説明文は、選択中モデル専用にする。
- モデル別設定欄の説明文も、選択中モデル専用にする。
- `5. 学習`タブにも、選択中モデルの説明を表示する。
- Target model、Task、Output nameなどのヘルプに、古いモデル前提の文章を残さない。
- 例: Wan2.2選択中に「Z-Image-Turbo」や「Ver 1.0ではZ-Imageのみ」のような文が出ないこと。

## 4. 必要ファイルはAdapterで定義する

- `model_adapters.py`で、そのモデルに必要なファイルを`required_setting_keys()`に定義する。
- 任意ファイルは`optional_setting_keys()`に分ける。
- 「実質必須」のファイルを任意扱いにしない。
- Settingsの入力欄、ヘルプ文、保存後ログ、Preflight、Command Previewで同じ必須項目になるよう揃える。

### Wan2.2での教訓

Wan2.2 t2v-A14Bでは、以下4つを必須扱いにする。

- `wan_vae`
- `wan_t5`
- `wan_dit`
- `wan_dit_high_noise`

`wan_dit_high_noise`を任意扱いにすると、UI上は保存できても、実運用の理解とズレる。

## 5. 保存後ログ・設定確認は選択中profileで実行する

- `設定を保存`後のログは、保存した`ui.target_model`を使って環境チェックする。
- `設定を確認`も、現在選択中のTarget modelを使う。
- `check_environment()`や`validate_settings_paths()`の呼び出しで、暗黙のデフォルト`z-image`に落ちないようにする。
- 保存後ログに、選択していないモデル名が出ないことを確認する。

確認例:

```text
Target model = Wan2.2
設定を保存
→ Profile: Wan2.2
→ ## Wan2.2 model files
```

NG例:

```text
Target model = Wan2.2
設定を保存
→ Profile: Z-Image / Z-Image-Turbo
→ ## Z-Image / Z-Image-Turbo model files
```

## 6. musubi-tuner側スクリプトもモデル別に確認する

- Z-Imageなら`zimage_train_network.py`、`zimage_cache_latents.py`、`zimage_cache_text_encoder_outputs.py`を確認する。
- Wan2.2なら`wan_train_network.py`、`wan_cache_latents.py`、`wan_cache_text_encoder_outputs.py`を確認する。
- 新モデルを追加したら、そのモデルのcache/trainスクリプトを環境チェックに追加する。

## 7. コマンド生成はAdapter経由に統一する

- Command PreviewはモデルごとのAdapterを通す。
- PreflightもAdapterを通す。
- Training実行も、選択中Target modelから生成したコマンドを使う。
- `z-image`固定の分岐や文言を残さない。

## 8. デフォルトパスとダウンロード手順を同時に整備する

- 新モデルを追加したら、必要ファイルのダウンロード手順も用意する。
- `settings_io.py`のデフォルトパスを実際のダウンロード構成に合わせる。
- `configs/settings.example.toml`も同じ構成にする。
- READMEまたはdocsに、Hugging Faceリポジトリ名、保存先、確認コマンドを書く。

## 9. UI回帰テスト手順

新モデル追加後は、最低限以下を手動確認する。

1. 起動する。
2. `Settings`でTarget modelを新モデルに変更する。
3. 上部説明文が新モデル用になる。
4. 右側のモデル別設定欄が新モデル用だけになる。
5. 不要な旧モデル項目が表示されない。
6. `設定を確認`で新モデル名が出る。
7. `設定を保存`後のログで新モデル名が出る。
8. `5. 学習`タブのTarget modelが新モデルに同期する。
9. Taskが新モデル用になる。
10. Command Previewが新モデル用コマンドになる。
11. Preflight Checkが新モデル用の必須ファイルを確認する。
12. ウインドウが縦に伸びすぎない。

## 10. 禁止事項

- 新モデルの項目を既存Settings画面へ単純に縦追加しない。
- 選択中ではないモデルの説明文を表示しない。
- 保存後ログを`z-image`デフォルトで実行しない。
- 新モデル追加後に、READMEやexample設定を古いパスのまま残さない。
- 実運用で必要なファイルを「任意」として扱わない。

このチェックリストを満たしてから、新モデル追加を完了扱いにする。

# UI flow

Musubi LoRA Factory は、設定項目を並べるだけのGUIではなく、作業手順を明示するステップ式UIを目指す。

## Principle

ユーザーが迷わないように、常に次を表示する。

```text
これをやる
↓
次はこれ
↓
終わったらこれ
```

## Current steps

### 1. Dataset

目的:
- 画像フォルダを指定する
- 画像枚数を確認する
- 解像度を確認する
- caption未作成数を確認する

次:
- caption未作成があれば `Generate Captions`
- captionがあれば `Caption Editor`

### 2. Caption / Review

目的:
- captionを一覧で確認する
- 不要語を削除する
- 一括置換する
- 保存する

次:
- `Build dataset.toml`

### 3. Config

目的:
- musubi-tuner用のdataset.tomlを作る

次:
- `Preview Commands`

### 4. Train

目的:
- 実行前にコマンドを確認する
- latent cacheを作る
- text encoder cacheを作る
- LoRA学習を行う

現状:
- `Preview Commands` は実装済み
- `Create Cache` と `Train LoRA` はまだdry-run/preview中心

次:
- PGX上でパス確認後、実行コマンド接続

### 5. Export

目的:
- 完成したLoRAをComfyUIへコピーする

次:
- ComfyUIで生成テスト

## Future UI

- step status indicator
- automatic current-step detection
- command preview with copy buttons
- run confirmation dialog
- progress log streaming
- GPU/memory dashboard

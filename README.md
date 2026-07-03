# Musubi LoRA Factory

PGX向けのローカルLoRA作成アプリのMVPです。

目的:
- データセット選択
- JoyCaption/LLM整形用のキャプション生成パイプライン
- caption一覧編集
- dataset.toml自動生成
- musubi-tunerのcache/trainコマンド実行
- 完成LoRAをComfyUIへコピー

> まだMVP雛形です。musubi-tunerの実際のコマンド引数は、PGX上のインストール状態に合わせて調整します。

## 起動

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

ブラウザで表示されたURLを開きます。

## 初期設定

`configs/settings.example.toml` を `configs/settings.toml` にコピーして、パスをPGX環境に合わせて変更してください。

```bash
cp configs/settings.example.toml configs/settings.toml
```

## 基本フロー

1. `Dataset` で画像フォルダを指定
2. `Check Dataset` で画像数・サイズ・caption有無を確認
3. `Generate Captions` で `.txt` captionを生成
4. `Caption Editor` でcaptionを確認・修正
5. `Config` で `dataset.toml` を作成
6. `Train` でcache作成・学習を実行
7. `Export` で完成LoRAをComfyUIへコピー

## Caption

`joycaption_command` を設定するとJoyCaptionを外部コマンドとして呼び出します。

```toml
joycaption_command = "python /opt/JoyCaption/caption.py --image {image}"
```

LLMはOpenAI互換APIを想定しています。

```toml
llm_endpoint = "http://localhost:8000/v1/chat/completions"
llm_model = "qwen-caption-helper"
```

# Musubi LoRA Factory

PGX向けのローカルLoRA作成アプリのMVPです。

目的:
- データセット選択
- JoyCaption/LLM整形用のキャプション生成パイプライン
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

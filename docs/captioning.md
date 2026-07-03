# Captioning design

## Goal

LoRA学習用のcaption作成を自動化する。

基本方針:

```text
image
  -> JoyCaption raw caption
  -> local LLM cleanup
  -> concise English tags
  -> image_name.txt
```

## Modes

- `joycaption_llm`: JoyCaptionで一次captionを作り、LLMで用途別に整形する
- `joycaption_only`: JoyCaption出力を簡易クリーンアップして保存する
- `llm_only`: 将来のVLM/LLM直接caption用
- `manual`: 手動captionを前提にする

## Part-specific cleanup

### eye
残す:
- iris color
- eyelids
- eyelashes
- eye shape
- gaze
- pupils
- eye makeup

消す:
- hair
- clothes
- background
- age
- gender
- full-face description

### mouth
残す:
- lips
- mouth shape
- smile
- teeth visibility
- lipstick
- expression around mouth

消す:
- eyes
- hair
- clothes
- background

## JoyCaption command

`configs/settings.toml` の `joycaption_command` に外部コマンドを設定する。

例:

```toml
joycaption_command = "python /opt/JoyCaption/caption.py --image {image}"
```

`{image}` は対象画像パスに置換される。

## Local LLM endpoint

OpenAI互換APIを想定する。

例:

```toml
llm_endpoint = "http://localhost:8000/v1/chat/completions"
llm_model = "qwen-caption-helper"
```

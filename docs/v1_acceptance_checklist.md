# Musubi LoRA Factory Ver 1.0 Acceptance Checklist

Ver 1.0の完成条件は、PGX上でZ-Image / Z-Image-Turbo用LoRAを最後まで作れることです。

## Scope

Ver 1.0はZ-Image専用です。

- Target model: `z-image`
- Task/profile: `z-image`
- Wan2.2、FLUX、SDXL、その他モデルはVer 1.0では対象外です。

## PGX setup

```bash
git clone https://github.com/onotakatoshi/Musubi_LoRA_Factory.git
cd Musubi_LoRA_Factory
chmod +x scripts/setup.sh scripts/start.sh scripts/check.sh scripts/update.sh scripts/create_desktop_launcher.sh
./scripts/setup.sh
./scripts/check.sh
./scripts/create_desktop_launcher.sh
```

## Launch check

- [ ] Desktop icon can be double-clicked
- [ ] PySide6 window opens
- [ ] UI language defaults to Japanese
- [ ] Settings tab opens without error
- [ ] System tab opens without error
- [ ] Dataset tab opens without error
- [ ] Caption編集 tab opens without error
- [ ] 画像プレビュー tab opens without error
- [ ] 設定生成 tab opens without error
- [ ] 学習 tab opens without error
- [ ] 書き出し tab opens without error

## Settings check

- [ ] musubi-tuner repo path is set
- [ ] musubi python path is set
- [ ] datasets dir is set
- [ ] outputs dir is set
- [ ] ComfyUI loras dir is set
- [ ] Z-Image DiT path is set
- [ ] Z-Image VAE path is set
- [ ] Z-Image text encoder path is set
- [ ] Validate Settings shows no missing required items
- [ ] Environment Check passes required Z-Image items

## Dataset check

- [ ] Dataset folder can be selected
- [ ] Dataset診断 shows image count
- [ ] Dataset診断 shows caption count
- [ ] Dataset診断 detects missing captions
- [ ] Dataset診断 detects duplicate candidates
- [ ] Caption診断 runs
- [ ] Caption編集 can load captions
- [ ] Caption編集 can save captions
- [ ] 画像プレビュー can show images
- [ ] 画像プレビュー can edit and save one caption

## Config check

- [ ] dataset.toml can be generated
- [ ] dataset.toml path is shown in the GUI
- [ ] generated dataset.toml points to the selected dataset folder
- [ ] generated cache directory exists

## Training check

- [ ] Target model is z-image
- [ ] Task/profile is z-image
- [ ] Preset適用 works
- [ ] 学習前レビュー runs
- [ ] Preflight Check passes
- [ ] Command Preview generates Z-Image commands
- [ ] Latent Cache command starts
- [ ] Text Cache command starts
- [ ] Train command starts
- [ ] Logs are visible in the GUI
- [ ] Stop button can request termination

## Output / Export check

- [ ] LoRA `.safetensors` is created
- [ ] Export copies LoRA to ComfyUI loras folder
- [ ] ComfyUI can see the copied LoRA
- [ ] Z-Image-Turbo workflow can load the LoRA
- [ ] Generated image reflects the trained concept/style/part

## Ver 1.0 done

Ver 1.0 is complete only when the full flow succeeds on PGX:

```text
setup
→ double-click launch
→ settings
→ dataset
→ caption check/edit
→ dataset.toml
→ latent cache
→ text cache
→ train
→ LoRA output
→ copy to ComfyUI
→ use in Z-Image-Turbo generation
```

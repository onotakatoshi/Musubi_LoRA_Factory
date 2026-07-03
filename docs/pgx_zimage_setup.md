# PGX Z-Image setup notes

This is the first-run setup guide for the Z-Image profile.

## 1. Clone

```bash
git clone https://github.com/onotakatoshi/Musubi_LoRA_Factory.git
cd Musubi_LoRA_Factory
```

## 2. Setup

```bash
chmod +x scripts/setup.sh scripts/start.sh
./scripts/setup.sh
```

## 3. Edit settings

Edit `configs/settings.toml`.

Important paths:

```toml
[musubi]
repo_path = "/home/ono/musubi-tuner"
python_path = "/home/ono/musubi-tuner/.venv/bin/python"

[paths]
datasets_dir = "/home/ono/datasets/lora"
outputs_dir = "/home/ono/outputs/lora"
comfyui_loras_dir = "/home/ono/ComfyUI/models/loras"

[model_paths]
zimage_dit = "/home/ono/models/z-image/z_image_base_or_deturbo.safetensors"
zimage_vae = "/home/ono/models/z-image/ae.safetensors"
zimage_text_encoder = "/home/ono/models/z-image/qwen3_text_encoder_00001-of-00002.safetensors"
zimage_base_weights = ""
```

`zimage_base_weights` is optional.

## 4. Start GUI

```bash
./scripts/start.sh
```

Open:

```text
http://localhost:7865
```

or from another machine:

```text
http://PGX_IP_ADDRESS:7865
```

## 5. First test settings

```text
Dataset: 20-100 high quality 512x512 images
LoRA type: eye
Target model: z-image
Rank: 16
Alpha: 16
Epochs: 10
Learning rate: 0.00005
Output name: eye_lora_zimage
```

## 6. GUI order

```text
Dataset
-> Check Dataset
-> Generate Captions
-> Caption Editor
-> Build dataset.toml
-> Target model: z-image
-> Preflight Check
-> Preview Commands
-> Run 1: Latent Cache
-> Run 2: Text Cache
-> Run 3: Train
-> Export
```

## 7. First-run rule

Do not start real training until Preflight Check is clear and Preview Commands looks correct.

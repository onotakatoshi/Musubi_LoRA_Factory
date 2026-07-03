# Z-Image command profile

This profile is for Z-Image / Z-Image-Turbo workflows through musubi-tuner.

## Current priority

The project currently prioritizes Z-Image before Wan2.2.

Important note:

- Directly training on Turbo-style weights may be unstable.
- The recommended first profile is to train against Base or De-Turbo style DiT weights.
- The resulting LoRA can then be tested in a Z-Image-Turbo generation workflow.

## Required model paths

Edit `configs/settings.toml`:

```toml
[model_paths]
zimage_dit = "/home/ono/models/z-image/z_image_base_or_deturbo.safetensors"
zimage_vae = "/home/ono/models/z-image/ae.safetensors"
zimage_text_encoder = "/home/ono/models/z-image/qwen3_text_encoder_00001-of-00002.safetensors"
zimage_base_weights = ""
```

`zimage_base_weights` is optional.

## GUI flow

1. Dataset
2. Generate Captions
3. Caption Editor
4. Build dataset.toml
5. Target model: `z-image`
6. Preflight Check
7. Preview Commands
8. Run 1: Latent Cache
9. Run 2: Text Cache
10. Run 3: Train
11. Export to ComfyUI

## Latent cache

```bash
python src/musubi_tuner/zimage_cache_latents.py \
  --dataset_config path/to/dataset.toml \
  --vae path/to/ae.safetensors
```

## Text encoder cache

```bash
python src/musubi_tuner/zimage_cache_text_encoder_outputs.py \
  --dataset_config path/to/dataset.toml \
  --text_encoder path/to/text_encoder.safetensors \
  --batch_size 16 \
  --fp8_llm
```

## Training

```bash
accelerate launch --num_cpu_threads_per_process 1 --mixed_precision bf16 \
  src/musubi_tuner/zimage_train_network.py \
  --dit path/to/z_image_base_or_deturbo.safetensors \
  --vae path/to/ae.safetensors \
  --text_encoder path/to/text_encoder.safetensors \
  --dataset_config path/to/dataset.toml \
  --sdpa \
  --mixed_precision bf16 \
  --timestep_sampling shift \
  --weighting_scheme none \
  --discrete_flow_shift 2.0 \
  --optimizer_type adamw8bit \
  --learning_rate 0.00005 \
  --gradient_checkpointing \
  --max_data_loader_n_workers 2 \
  --persistent_data_loader_workers \
  --network_module networks.lora_zimage \
  --network_dim 16 \
  --network_alpha 16 \
  --fp8_base \
  --fp8_scaled \
  --fp8_llm \
  --max_train_epochs 10 \
  --save_every_n_epochs 1 \
  --seed 42 \
  --output_dir path/to/output \
  --output_name eye_lora_zimage
```

## First recommended settings

For a first test:

```text
Dataset: 20-100 images
Resolution: 512
Rank: 16
Alpha: 16
Epochs: 10
Learning rate: 0.00005
Target: z-image
```

## Next work

- Add Z-Image presets to the UI
- Add separate `Z-Image Base` / `Z-Image De-Turbo` / `Z-Image Turbo Test` modes
- Add ComfyUI test workflow export

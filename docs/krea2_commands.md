# Krea 2 command profile

Krea 2 image LoRA training through musubi-tuner.

Upstream reference: `musubi-tuner/docs/krea2.md`.

## Download

```bash
bash ./scripts/download_model_assets.sh krea2
```

This pulls three files from [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2):
the RAW DiT, the Qwen-Image VAE and the Qwen3-VL-4B text encoder.

The official [krea/Krea-2-Raw](https://huggingface.co/krea/Krea-2-Raw) repository is
gated behind a manually maintained authorized list, and being able to read its metadata
does not mean you can download from it. The Comfy-Org mirror carries the same 26.28GB
bf16 weights with no gate.

## Train on RAW, not Turbo

musubi-tuner's documentation is explicit: *"Train on the **RAW** DiT."* Turbo is the
distilled few-step checkpoint and belongs to inference, the same split as Z-Image Base
versus Turbo. Apply the finished LoRA to Turbo when generating.

Nothing in a checkpoint's tensors distinguishes a RAW-derived community mix from a
Turbo-derived one — the architecture is identical. That is why the app's autofill only
proposes files named `krea2_raw_*` or `raw.safetensors` and never scans a ComfyUI tree
for the DiT.

## Required model paths

```toml
[model_paths]
krea2_dit = "../models/krea2/Comfy-Org/Krea-2/diffusion_models/krea2_raw_bf16.safetensors"
krea2_vae = "../models/krea2/Comfy-Org/Krea-2/vae/qwen_image_vae.safetensors"
krea2_text_encoder = "../models/krea2/Comfy-Org/Krea-2/text_encoders/qwen3vl_4b_bf16.safetensors"
krea2_base_weights = ""
```

- The VAE is the **Qwen-Image** VAE. If you already have it for Qwen-Image, point at that.
- The text encoder must be a single safetensors **file**, not a HuggingFace directory.
- `krea2_base_weights` is optional: a LoRA merged into the base before training.

## Accepted DiT formats

| file | flag needed |
| --- | --- |
| `krea2_raw_bf16.safetensors` | none (default) |
| `krea2_raw_fp8_scaled.safetensors` | `--fp8_base --fp8_scaled` (both, or fp8 is rejected) |
| `krea2_raw_int8_convrot.safetensors` | `--convrot_int8` |

The app generates the bf16 path. On PGX there is no reason to quantize: bf16 is the most
accurate and the memory is there. The quantized variants mainly help GPUs without fp8
support.

ConvRot INT8 checkpoints are recognised by carrying `weight` int8 + `weight_scale` +
`comfy_quant` tensors. An int8 file **without** `comfy_quant` is some other quantization
and is not known to load.

## Why --timestep_sampling krea2_shift

The upstream example uses `--timestep_sampling shift --discrete_flow_shift 2.5`, and 2.5
is the K2 inference time-shift **at 1024x1024**. The schedule is resolution-aware: about
1.6 at 256x256 rising to 3.2 at 1280x1280.

Baking in 2.5 would therefore be wrong for anyone who picks another resolution in the
Config tab. `krea2_shift` reproduces the per-sample resolution-aware schedule instead,
so it is correct at whatever resolution the dataset uses, and no fixed
`--discrete_flow_shift` is needed.

## GUI flow

1. Dataset
2. Caption editor (generate captions with Qwen2.5-VL if needed)
3. Build dataset.toml
4. Target model: `Krea 2`
5. Preflight Check
6. Run 1: Latent Cache
7. Run 2: Text Cache
8. Run 3: Train
9. Export to ComfyUI

Selecting Krea 2 fills in rank 32 / alpha 32 / lr 1e-4, which is the model authors'
recommended default per the upstream docs.

## Latent cache

```bash
python src/musubi_tuner/krea2_cache_latents.py \
  --dataset_config /path/to/dataset.toml \
  --vae /path/to/qwen_image_vae.safetensors
```

Image datasets only. Krea 2 is plain text-to-image, so only target latents are cached.

## Text encoder cache

```bash
python src/musubi_tuner/krea2_cache_text_encoder_outputs.py \
  --dataset_config /path/to/dataset.toml \
  --text_encoder /path/to/qwen3vl_4b_bf16.safetensors \
  --batch_size 1
```

Krea 2 caches a multi-layer hidden-state stack from Qwen3-VL, storing only non-padding
tokens. Raise `--batch_size` if you have memory to spare.

## Train

```bash
python -m accelerate.commands.launch --num_cpu_threads_per_process 1 --mixed_precision bf16 \
  src/musubi_tuner/krea2_train_network.py \
  --dit /path/to/krea2_raw_bf16.safetensors \
  --vae /path/to/qwen_image_vae.safetensors \
  --dataset_config /path/to/dataset.toml \
  --sdpa --mixed_precision bf16 \
  --timestep_sampling krea2_shift --weighting_scheme none \
  --optimizer_type adamw8bit --learning_rate 1e-4 \
  --gradient_checkpointing --max_data_loader_n_workers 2 --persistent_data_loader_workers \
  --network_module networks.lora_krea2 --network_dim 32 --network_alpha 32 \
  --max_train_epochs 16 --save_every_n_epochs 1 --seed 42 \
  --output_dir /path/to/output --output_name krea2-lora
```

`--text_encoder` is not passed to training: the text encoder outputs are pre-cached, and
it is only needed if you generate sample images during the run.

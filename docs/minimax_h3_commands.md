# MiniMax-H3 command profile

MiniMax-H3 text-to-video-with-audio (T2VA) LoRA training through musubi-tuner.

Upstream reference: `musubi-tuner/docs/minimax_h3.md`. Read and accept the
[MiniMax-H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
before downloading the weights.

## Download

```bash
bash ./scripts/download_model_assets.sh minimax-h3
```

Only the BF16 set is fetched (the repository also publishes pruned, ConvRot INT8 and
NVFP4+AWQ variants). Those variants are drop-in replacements: point `minimax_h3_dit` or
`minimax_h3_text_encoder` at one and nothing else changes.

## Required model paths

```toml
[model_paths]
minimax_h3_dit = "../models/minimax-h3/Comfy-Org/MiniMax-H3/diffusion_models/minimax_h3_fl2va_bf16.safetensors"
minimax_h3_text_encoder = "../models/minimax-h3/Comfy-Org/MiniMax-H3/text_encoders/qwen3vl_32b_minimax_h3_bf16.safetensors"
minimax_h3_video_vae = "../models/minimax-h3/Comfy-Org/MiniMax-H3/vae/minimax_h3_video_vae_fp16.safetensors"
minimax_h3_audio_vae = "../models/minimax-h3/Comfy-Org/MiniMax-H3/vae/minimax_h3_audio_vae_fp32.safetensors"
minimax_h3_base_weights = ""
```

- The audio VAE is required even when the dataset has no audio: H3 always carries audio rows.
- T2VA and FL2VA use the **FL2VA** transformer. Ref2VA needs the Ref2VA transformer instead.
- `minimax_h3_base_weights` is optional and selects a different training recipe (below).

## Training recipe

The released H3 checkpoints are CFG-distilled, so plain flow-matching training pulls the
model out of its guided space and degrades as it runs. musubi-tuner therefore does not
offer plain flow training, and this app picks one of the two self-contained recipes:

| `minimax_h3_base_weights` | Recipe | What the app adds |
| --- | --- | --- |
| empty (default) | Guidance loss | `--uncond_output` on the text cache, then `--h3_guidance_loss_scale 4.0 --h3_guidance_loss_sigma_min 0.15 --h3_guidance_loss_uncond_cache` on train |
| set to a de-distillation adapter | Training adapter | `--base_weights <adapter>` on train, no guidance flags |

Guidance loss costs about one extra no-grad forward on ~85% of steps and needs no
third-party file. The training adapter has no extra forward but needs an adapter you
supply, and the LoRA it produces is used on the plain base at inference.

Teacher matching is the third upstream recipe. It is not wired into the GUI yet; run it
by hand from `musubi-tuner/docs/minimax_h3.md` if you need it.

## Dataset constraints

These come from H3 itself and the GUI does not relax them:

- 24 fps target. Width and height must be positive multiples of 32.
- Frame count must be `17*n+5`; the released range is 124 to 345 frames (5 to 15 seconds).
- Audio, when present, is decoded as stereo 32000 Hz.

## GUI flow

1. Dataset
2. Caption editor
3. Build dataset.toml
4. Target model: `MiniMax-H3`
5. Preflight Check
6. Preview Commands
7. Run 1: Latent Cache
8. Run 2: Text Cache
9. Run 3: Train
10. Export to ComfyUI

## Latent cache

```bash
python src/musubi_tuner/minimax_h3_cache_latents.py \
  --dataset_config /path/to/dataset.toml \
  --task t2va \
  --video_vae /path/to/minimax_h3_video_vae_fp16.safetensors \
  --audio_vae /path/to/minimax_h3_audio_vae_fp32.safetensors \
  --cache_seed 42 \
  --skip_existing
```

## Text encoder cache

```bash
python src/musubi_tuner/minimax_h3_cache_text_encoder_outputs.py \
  --dataset_config /path/to/dataset.toml \
  --task t2va \
  --text_encoder /path/to/qwen3vl_32b_minimax_h3_bf16.safetensors \
  --text_cache_dtype bf16 \
  --skip_existing \
  --text_encoder_blocks_to_swap 50 \
  --uncond_output /path/to/output/h3_uncond.safetensors
```

Drop `--uncond_output` when using the training-adapter recipe.

## Train

```bash
python -m accelerate.commands.launch --num_cpu_threads_per_process 1 --mixed_precision bf16 \
  src/musubi_tuner/minimax_h3_train_network.py \
  --dataset_config /path/to/dataset.toml \
  --task t2va \
  --dit /path/to/minimax_h3_fl2va_bf16.safetensors \
  --sdpa --mixed_precision bf16 \
  --timestep_sampling uniform --weighting_scheme none --discrete_flow_shift 1.0 \
  --optimizer_type adamw8bit --learning_rate 1e-4 \
  --gradient_checkpointing --max_data_loader_n_workers 2 --persistent_data_loader_workers \
  --network_module networks.lora_minimax_h3 --network_dim 16 --network_alpha 16 \
  --max_train_epochs 16 --save_every_n_epochs 1 --seed 42 \
  --output_dir /path/to/output --output_name h3_lora \
  --blocks_to_swap 48 \
  --h3_guidance_loss_scale 4.0 \
  --h3_guidance_loss_sigma_min 0.15 \
  --h3_guidance_loss_uncond_cache /path/to/output/h3_uncond.safetensors
```

`--timestep_sampling uniform`, `--weighting_scheme none` and `--discrete_flow_shift 1.0`
are the only values musubi-tuner accepts for H3: the model draws one base time per item
and derives the video and audio sigmas from it with its own shifts (12 and 3).

Lower `--blocks_to_swap` if you have memory headroom; raise it if training OOMs.

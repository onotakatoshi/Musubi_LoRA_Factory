# Wan2.2 command profile

This profile follows musubi-tuner's Wan2.1/2.2 flow:

1. latent cache
2. text encoder cache
3. LoRA training

Wan2.2 14B uses two DiT models:

- low noise DiT
- high noise DiT

The paths are configured in `configs/settings.toml`.

```toml
[model_paths]
wan_vae = "/home/ono/models/wan/Wan2.1_VAE.pth"
wan_t5 = "/home/ono/models/wan/models_t5_umt5-xxl-enc-bf16.pth"
wan_dit = "/home/ono/models/wan/wan2.2_low_noise.safetensors"
wan_dit_high_noise = "/home/ono/models/wan/wan2.2_high_noise.safetensors"
```

## Latent cache

```bash
python src/musubi_tuner/wan_cache_latents.py \
  --dataset_config path/to/dataset.toml \
  --vae path/to/Wan2.1_VAE.pth
```

For I2V, add:

```bash
--i2v
```

## Text encoder cache

```bash
python src/musubi_tuner/wan_cache_text_encoder_outputs.py \
  --dataset_config path/to/dataset.toml \
  --t5 path/to/models_t5_umt5-xxl-enc-bf16.pth \
  --batch_size 16
```

## Training

```bash
accelerate launch --num_cpu_threads_per_process 1 --mixed_precision bf16 \
  src/musubi_tuner/wan_train_network.py \
  --task t2v-A14B \
  --dit path/to/wan2.2_low_noise.safetensors \
  --dit_high_noise path/to/wan2.2_high_noise.safetensors \
  --dataset_config path/to/dataset.toml \
  --sdpa --mixed_precision bf16 \
  --optimizer_type adamw8bit \
  --learning_rate 0.00005 \
  --gradient_checkpointing \
  --max_data_loader_n_workers 2 \
  --persistent_data_loader_workers \
  --network_module networks.lora_wan \
  --network_dim 16 \
  --network_alpha 16 \
  --timestep_sampling shift \
  --discrete_flow_shift 12.0 \
  --preserve_distribution_shape \
  --force_v2_1_time_embedding \
  --offload_inactive_dit \
  --max_train_epochs 10 \
  --save_every_n_epochs 1 \
  --seed 42 \
  --output_dir path/to/output \
  --output_name eye_lora_wan22
```

## Notes

- For `i2v-A14B`, use `--discrete_flow_shift 5.0` as the initial profile.
- For `t2v-A14B`, use `--discrete_flow_shift 12.0` as the initial profile.
- These are starting profiles, not final optimal values.

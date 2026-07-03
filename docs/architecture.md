# Architecture

Musubi LoRA Factory is designed as a model-profile based desktop application.

## Ver 1.0 policy

Ver 1.0 focuses on Z-Image / Z-Image-Turbo LoRA generation.

However, the application must not be hard-coded as a permanently Z-Image-only app.

The rule is:

> UI scope is Z-Image-only in Ver 1.0. Internal structure remains model-profile based.

This prevents large rewrites when Wan2.2 and other LoRA targets are added later.

## Model profile layer

Model availability is defined in `app/model_registry.py`.

Each profile has:

- `id`
- `display_name`
- `task`
- `enabled_in_v1`
- Japanese/English description

Ver 1.0 shows only profiles with `enabled_in_v1=True`.

Future model support should be added by adding or enabling a profile, then implementing the required command builder and settings fields.

## UI rule

Do not scatter model-specific choices throughout the GUI.

Good:

```python
from model_registry import enabled_profiles
```

Bad:

```python
if target_model == "wan2.2":
    ...
```

except inside model-specific adapter modules.

## Command generation rule

Command generation should go through profile-aware functions.

Ver 1.0 currently implements Z-Image command generation only.

When adding Wan2.2:

1. Enable `wan2.2` in `model_registry.py`
2. Add/restore Wan2.2 model path validation
3. Add Wan2.2 command builder adapter
4. Add Wan2.2-specific preset values
5. Add Wan2.2 acceptance checklist

## Settings rule

Settings may contain future model path sections, but Ver 1.0 UI should only require Z-Image paths.

Future paths can remain in `settings.toml` as inactive fields.

## Acceptance rule

A model is not considered supported until the full flow works:

```text
settings
→ dataset
→ caption check/edit
→ dataset.toml
→ cache
→ train
→ LoRA output
→ ComfyUI generation test
```

For Ver 1.0 this full flow is required only for Z-Image / Z-Image-Turbo.

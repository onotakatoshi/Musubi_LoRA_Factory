from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CaptionResult:
    raw_caption: str
    cleaned_caption: str


LORA_FOCUS_PROMPTS: dict[str, str] = {
    "eye": "Keep only eye-related tags: iris color, eyelids, eyelashes, eye shape, gaze, pupils, makeup. Remove hair, clothes, background, age, gender, and full-face descriptions.",
    "mouth": "Keep only mouth-related tags: lips, mouth shape, smile, teeth visibility, lipstick, expression around mouth. Remove eyes, hair, clothes, background, age, and gender.",
    "face": "Keep only face identity, expression, skin, facial structure, and makeup. Remove clothes and background.",
    "hair": "Keep only hair-related tags: color, length, bangs, style, texture, volume. Remove face, clothes, and background.",
    "hand": "Keep only hand-related tags: hand pose, fingers, nails, gesture, skin details. Remove face, clothes, and background.",
    "style": "Keep only style-related tags: rendering style, lighting, color palette, medium, texture, composition, mood.",
    "clothing": "Keep only clothing-related tags: garment type, color, fabric, pattern, accessories. Remove face, hair, and background.",
}

NEGATIVE_WORDS: dict[str, set[str]] = {
    "eye": {"hair", "shirt", "dress", "background", "room", "wall", "woman", "man", "girl", "boy", "face", "portrait"},
    "mouth": {"eye", "eyes", "hair", "shirt", "dress", "background", "room", "wall", "woman", "man", "girl", "boy"},
    "hair": {"shirt", "dress", "background", "room", "wall"},
    "hand": {"face", "eyes", "hair", "shirt", "dress", "background", "room", "wall"},
}


def simple_tag_cleanup(text: str, lora_type: str) -> str:
    text = text.replace("\n", ", ").replace(";", ",")
    parts = [p.strip().strip(".") for p in text.split(",")]
    banned = NEGATIVE_WORDS.get(lora_type, set())
    cleaned: list[str] = []
    for part in parts:
        if not part:
            continue
        lower = part.lower()
        if any(word in lower.split() or word in lower for word in banned):
            continue
        if part not in cleaned:
            cleaned.append(part)
    return ", ".join(cleaned[:24])


def run_joycaption_cli(image_path: Path, joycaption_command: str) -> str:
    """Run an external JoyCaption command.

    The command may include {image}. Example:
    python /opt/JoyCaption/caption.py --image {image}
    """
    if not joycaption_command.strip():
        return ""
    cmd = joycaption_command.replace("{image}", str(image_path))
    proc = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout)
    return proc.stdout.strip()


def refine_caption_with_llm(raw_caption: str, lora_type: str, endpoint: str, model: str) -> str:
    if not endpoint or not model:
        return simple_tag_cleanup(raw_caption, lora_type)

    focus = LORA_FOCUS_PROMPTS.get(lora_type, LORA_FOCUS_PROMPTS["style"])
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You clean image captions for LoRA training. Return only concise English comma-separated tags. No explanations.",
            },
            {
                "role": "user",
                "content": f"Task: {focus}\nRaw caption: {raw_caption}\nCleaned tags:",
            },
        ],
        "temperature": 0.1,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return simple_tag_cleanup(raw_caption, lora_type) + f"  # LLM fallback: {exc}"

    content = result["choices"][0]["message"]["content"]
    return simple_tag_cleanup(content, lora_type)


def caption_one_image(
    image_path: Path,
    lora_type: str,
    mode: str,
    joycaption_command: str,
    llm_endpoint: str,
    llm_model: str,
) -> CaptionResult:
    raw = ""
    if mode in {"joycaption_llm", "joycaption_only"}:
        raw = run_joycaption_cli(image_path, joycaption_command)
    elif mode == "llm_only":
        raw = image_path.stem.replace("_", " ")
    else:
        raw = ""

    if not raw:
        raw = f"high quality {lora_type} detail, sharp focus"

    if mode == "joycaption_only":
        cleaned = simple_tag_cleanup(raw, lora_type)
    elif mode in {"joycaption_llm", "llm_only"}:
        cleaned = refine_caption_with_llm(raw, lora_type, llm_endpoint, llm_model)
    else:
        cleaned = raw

    return CaptionResult(raw_caption=raw, cleaned_caption=cleaned)

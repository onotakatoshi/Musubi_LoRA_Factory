"""Shared rules for which weight files musubi-tuner can actually load.

musubi-tuner loads split weights by filename pattern (``-00001-of-0000N.safetensors``),
see ``utils/safetensors_utils.get_split_weight_filenames``. It has no reader for a
``*.safetensors.index.json`` manifest, so pointing a model path at one fails at load
time with ``SafetensorError: HeaderTooLarge`` even though the file exists.

Every model-path detector in this app goes through here so the same regression
cannot come back from a different entry point.
"""

from __future__ import annotations

import re
from pathlib import Path

INDEX_JSON_SUFFIX = ".index.json"
SHARD_RE = re.compile(r"^(?P<prefix>.*?)(?P<num>\d+)-of-(?P<count>\d+)\.safetensors$")

LOADABLE_SUFFIXES = {".safetensors", ".pth", ".pt", ".bin", ".ckpt"}


def is_index_json(path: Path | str) -> bool:
    return str(path).endswith(INDEX_JSON_SUFFIX)


def is_first_shard(path: Path | str) -> bool:
    match = SHARD_RE.match(Path(path).name)
    return bool(match) and int(match.group("num")) == 1


def _shard_sort_key(path: Path) -> tuple[int, str]:
    match = SHARD_RE.match(path.name)
    return (int(match.group("num")) if match else 0, path.name)


def first_shard_in_dir(directory: Path, prefix: str = "") -> Path | None:
    """Return the ``-00001-of-N`` shard in ``directory``, or a single safetensors."""
    if not directory.is_dir():
        return None
    shards = [p for p in directory.glob(f"{prefix}*-of-*.safetensors") if is_first_shard(p)]
    if shards:
        return sorted(shards, key=_shard_sort_key)[0]
    singles = [p for p in directory.glob(f"{prefix}*.safetensors") if not is_index_json(p)]
    if singles:
        return sorted(singles, key=lambda p: (len(p.name), p.name))[0]
    return None


def resolve_model_file(path: Path | str) -> Path | None:
    """Map whatever the user or a detector found onto a file musubi-tuner can load.

    ``*.safetensors.index.json`` becomes the matching first shard, a directory becomes
    the first shard inside it, and an already-loadable file is returned unchanged.
    Returns ``None`` when nothing usable is there.
    """
    candidate = Path(path)
    if is_index_json(candidate):
        # foo.safetensors.index.json -> foo-00001-of-0000N.safetensors (or foo.safetensors)
        stem = candidate.name[: -len(INDEX_JSON_SUFFIX)]
        stem = stem[: -len(".safetensors")] if stem.endswith(".safetensors") else stem
        resolved = first_shard_in_dir(candidate.parent, prefix=stem)
        return resolved
    if candidate.is_dir():
        return first_shard_in_dir(candidate)
    if candidate.is_file():
        return candidate
    return None


def format_problem(value: str) -> str | None:
    """Return a Japanese explanation when ``value`` is a path musubi-tuner cannot load."""
    if not value:
        return None
    path = Path(value)
    if is_index_json(path):
        hint = resolve_model_file(path)
        message = (
            f"{path.name} はsafetensorsの索引ファイルです。musubi-tunerは読み込めません。"
            "分割ファイルの先頭 (-00001-of-0000N.safetensors) を指定してください。"
        )
        if hint is not None:
            message += f"\n  候補: {hint}"
        return message
    if path.is_dir():
        hint = first_shard_in_dir(path)
        message = f"{path} はフォルダです。重みファイル自体を指定してください。"
        if hint is not None:
            message += f"\n  候補: {hint}"
        return message
    if path.suffix.lower() not in LOADABLE_SUFFIXES:
        return f"{path.name} は重みファイルとして想定されていない拡張子です ({path.suffix or 'なし'})。"
    return None

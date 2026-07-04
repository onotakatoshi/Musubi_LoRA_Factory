from __future__ import annotations

from pathlib import Path

import toml

from settings_io import default_settings, load_settings, save_settings

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "configs" / "settings.toml"
OLD_HOME_PREFIX = "/home/ono"


def _replace_old_home(value: str, home: str) -> str:
    if value == OLD_HOME_PREFIX:
        return home
    if value.startswith(OLD_HOME_PREFIX + "/"):
        return home + value[len(OLD_HOME_PREFIX):]
    return value


def fix_local_paths(settings_path: Path = SETTINGS_PATH) -> str:
    home = str(Path.home())
    if not settings_path.exists():
        save_settings(settings_path, default_settings())
        return f"Created settings with local home paths: {settings_path}"

    data = load_settings(settings_path)
    changed: list[str] = []
    for section in ["musubi", "paths", "model_paths"]:
        values = data.get(section, {})
        if not isinstance(values, dict):
            continue
        for key, value in list(values.items()):
            if not isinstance(value, str):
                continue
            updated = _replace_old_home(value, home)
            if updated != value:
                values[key] = updated
                changed.append(f"{section}.{key}: {value} -> {updated}")

    save_settings(settings_path, data)
    if not changed:
        return f"No /home/ono paths found. Settings unchanged: {settings_path}"
    return "Fixed local paths:\n" + "\n".join(changed)


def main() -> int:
    print(fix_local_paths())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

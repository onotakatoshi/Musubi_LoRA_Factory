from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "scripts" / "verify_pgx_beta.sh"


def main() -> int:
    text = VERIFY.read_text(encoding="utf-8")
    assert "python app/env_check_test.py" in text
    assert "python app/docs_static_check.py" in text
    assert "python app/create_sample_dataset.py" in text
    assert "/tmp/musubi_lora_factory_sample_dataset" in text
    assert "python app/beta_extension_files_check.py" in text
    print("PGX beta extra verification script static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

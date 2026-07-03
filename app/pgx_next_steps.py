from __future__ import annotations


def pgx_next_steps() -> str:
    return """# PGX Next Steps

Verify beta:
  cd Musubi_LoRA_Factory
  bash ./scripts/update.sh
  bash ./scripts/verify_pgx_beta.sh

Start GUI:
  bash ./scripts/start.sh

Collect debug info:
  bash ./scripts/collect_debug_info.sh

Validate output after training:
  bash ./scripts/validation_report.sh /path/to/output_dir eye_lora_zimage

GUI checks:
  System tab -> 環境チェック
  Train tab -> ログ解析
  Export tab -> コピー前チェック
"""


def main() -> int:
    print(pgx_next_steps())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

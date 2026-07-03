from __future__ import annotations

from verification_readiness import verification_readiness


def main() -> int:
    report = verification_readiness()
    assert report.startswith("# Verification Readiness")
    assert "OK: required beta files exist" in report
    assert "READY: PGX実機でZ-Image LoRAの通し検証に進めます。" in report, report
    assert "NOT READY" not in report, report
    print("Verification readiness test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

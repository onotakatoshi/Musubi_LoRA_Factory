from __future__ import annotations

from verification_readiness import is_ready_report, verification_readiness


def main() -> int:
    report = verification_readiness()
    assert report.startswith("# Verification Readiness")
    assert "OK: required beta files exist" in report
    assert is_ready_report(report), report
    assert not is_ready_report("NOT READY: PGX実機検証の前に修正が必要です。")
    print("Verification readiness test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from beta_status import beta_status, missing_required_files


def main() -> int:
    text = beta_status()
    assert "Beta Status" in text
    assert "Z-Image" in text
    assert "Enabled profiles" in text
    assert "Implemented adapters" in text
    assert "StageGuidance" in text
    assert "MusubiRuntimeCheck" in text
    assert "musubi_runtime_check_test.py" in text
    assert "VerificationReadiness" in text
    assert "verification_readiness.py" in text
    assert "Next PGX action" in text
    assert "python app/verification_readiness.py" in text
    assert missing_required_files() == []
    print("Beta status test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from stage_guidance import guidance_for_stage, stage_display_name, success_guidance_for_stage


def main() -> int:
    assert stage_display_name("latent_cache") == "Latent Cache"
    failed = guidance_for_stage("train", 1, "/tmp/train.log")
    assert "Train LoRA failed" in failed
    assert "Exit code: 1" in failed
    assert "Log file: /tmp/train.log" in failed
    assert "DiT" in failed
    assert "ログ解析" in failed

    ok = success_guidance_for_stage("text_cache", "/tmp/text.log")
    assert "Text Encoder Cache done" in ok
    assert "Train LoRA" in ok

    unknown = guidance_for_stage("unknown")
    assert "ログを確認" in unknown

    print("Stage guidance test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

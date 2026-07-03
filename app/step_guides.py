from __future__ import annotations

GUIDES = {
    "dataset": """# Step 1: Dataset

**目的**: 学習用画像フォルダを確認します。

**やること**:
1. Dataset folder を指定
2. Check Dataset を押す
3. 画像枚数、解像度、caption未作成数を見る

**完了条件**:
- 画像が見つかる
- 画像が概ね512x512以上
- caption未作成数を把握できている

**次に押すボタン**:
- captionが無ければ `Generate Captions`
- caption確認へ進むなら `Caption Editor` タブ
""",
    "caption": """# Step 2-3: Caption / Review

**目的**: 画像ごとのcaptionを確認・修正します。

**やること**:
1. Load Captions を押す
2. caption一覧を確認
3. 不要語があれば Remove Words / Bulk Replace
4. Save Captions を押す

**完了条件**:
- 画像ごとに .txt caption がある
- 学習対象と関係ない語が減っている

**次に押すボタン**:
- `Config` タブで `Build dataset.toml`
""",
    "config": """# Step 4: Config

**目的**: musubi-tuner用の dataset.toml を作ります。

**やること**:
1. Output folder を指定
2. Resolution を選ぶ
3. Build dataset.toml を押す

**完了条件**:
- dataset.toml path にパスが表示される

**次に押すボタン**:
- `Train` タブで `0. Preflight Check`
""",
    "train": """# Step 5: Train

**目的**: Z-Image用LoRAを3段階で学習します。

**やること**:
1. Target model が z-image であることを確認
2. 0. Preflight Check
3. Preview Commands
4. Run 1: Latent Cache
5. Run 2: Text Cache
6. Run 3: Train

**完了条件**:
- PreflightがOK
- cache 2種類が完了
- TrainがDONEで終了

**次に押すボタン**:
- `Export` タブで `Copy to ComfyUI`
""",
    "export": """# Step 6: Export

**目的**: 完成したLoRAをComfyUIへコピーします。

**やること**:
1. LoRA file path を指定
2. Copy to ComfyUI を押す

**完了条件**:
- ComfyUIのlorasフォルダに.safetensorsがコピーされる

**次にやること**:
- ComfyUIでZ-Image-TurboワークフローにLoRAを読み込んでテスト
""",
}


def guide(topic: str) -> str:
    return GUIDES.get(topic, "ガイドがまだ登録されていません。")

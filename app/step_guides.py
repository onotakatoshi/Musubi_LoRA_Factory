from __future__ import annotations

GUIDES_JA = {
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
- `Train` タブで学習を実行
""",
    "train": """# Step 5: Train

**目的**: Z-Image用LoRAを3段階で学習します。

**やること**:
1. Target model が z-image であることを確認
2. Run 1: Latent Cache
3. Run 2: Text Cache
4. Run 3: Train

**完了条件**:
- cache 2種類が完了
- TrainがDONEで終了

**次に押すボタン**:
- `Export` タブへ進む
""",
    "export": """# Step 6: Export

**目的**: 完成したLoRAをComfyUIへ配置します。

**やること**:
1. LoRA file path を指定
2. Copy to ComfyUI を押す

**完了条件**:
- ComfyUIのlorasフォルダに.safetensorsが配置される

**次にやること**:
- ComfyUIでLoRAを読み込んでテスト
""",
}

GUIDES_EN = {
    "dataset": """# Step 1: Dataset

**Purpose**: Check the folder that contains your training images.

**What to do**:
1. Select the Dataset folder
2. Click Check Dataset
3. Review image count, resolution, and missing caption count

**Done when**:
- Images are found
- Images are roughly 512x512 or larger
- You understand how many captions are missing

**Next**:
- Open the `Caption Editor` tab to review captions
""",
    "caption": """# Step 2-3: Caption / Review

**Purpose**: Review and edit captions for each image.

**What to do**:
1. Click Load Captions
2. Review the caption list
3. Use Remove Words or Bulk Replace when needed
4. Click Save Captions

**Done when**:
- Each image has a matching .txt caption
- Unrelated words have been reduced

**Next**:
- Open the `Config` tab and build dataset.toml
""",
    "config": """# Step 4: Config

**Purpose**: Create dataset.toml for musubi-tuner.

**What to do**:
1. Select the Output folder
2. Choose the Resolution
3. Click Build dataset.toml

**Done when**:
- The dataset.toml path field shows a generated path

**Next**:
- Open the `Train` tab and run the training steps
""",
    "train": """# Step 5: Train

**Purpose**: Train a Z-Image LoRA in three stages.

**What to do**:
1. Confirm the Target model
2. Run Latent Cache
3. Run Text Cache
4. Run Train

**Done when**:
- Both cache stages complete
- Train finishes successfully

**Next**:
- Open the `Export` tab
""",
    "export": """# Step 6: Export

**Purpose**: Place the completed LoRA where ComfyUI can use it.

**What to do**:
1. Select the LoRA file path
2. Click Copy to ComfyUI

**Done when**:
- The .safetensors file is placed in the ComfyUI LoRA folder

**Next**:
- Load and test the LoRA in ComfyUI
""",
}


def guide(topic: str, lang: str = "日本語") -> str:
    guides = GUIDES_EN if lang == "English" else GUIDES_JA
    fallback = "Guide is not registered yet." if lang == "English" else "ガイドがまだ登録されていません。"
    return guides.get(topic, fallback)

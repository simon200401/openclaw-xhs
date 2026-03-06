from __future__ import annotations

import json
from pathlib import Path


SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_xhs_posts.json"


def load_sample_posts() -> dict[str, list[dict]]:
    with SAMPLE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

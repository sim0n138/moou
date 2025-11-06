"""High score persistence utilities."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Tuple

APP_DIR_NAME = "Snake"
SCORE_FILE = "highscore.json"


def _get_base_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        base = Path(appdata) / APP_DIR_NAME
    else:
        base = Path.home() / f".{APP_DIR_NAME.lower()}"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _score_file() -> Path:
    return _get_base_dir() / SCORE_FILE


def load_highscore() -> int:
    try:
        with _score_file().open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return 0
    score = data.get("highscore", 0)
    if isinstance(score, int) and score >= 0:
        return score
    return 0


def save_highscore(score: int) -> None:
    if score < 0:
        return
    payload = {"highscore": int(score)}
    try:
        with _score_file().open("w", encoding="utf-8") as fh:
            json.dump(payload, fh)
    except OSError:
        pass

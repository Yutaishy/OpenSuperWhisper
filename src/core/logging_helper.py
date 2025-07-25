"""Logging helper utilities for Open Super Whisper.

このモジュールは 1 セッション分のログファイルをローカルに保存する責務を持ちます。

ログ構造: (LOG_BASE_DIR) / <session_id>/
  ├─ raw.txt           : ASR 素出力
  ├─ formatted.json    : PostFormatter の JSON 出力
  ├─ prompt.txt        : 使用した system prompt
  └─ meta.json         : 各種メタ情報 (モデル名・温度・レスポンス ID 等)
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

LOG_DIR_DEFAULT = Path(os.environ.get("OSW_BASE_DIR", r"C:\Users\yuta9\dev\voice_input")) / "logs"

__all__ = [
    "LOG_DIR_DEFAULT",
    "create_session_dir",
    "save_raw_text",
    "save_formatted_json",
    "save_prompt_text",
    "save_meta",
]


# ----------------------------------------------------------------------
# Session directory handling
# ----------------------------------------------------------------------

def create_session_dir(base_dir: Path | None = None) -> Path:
    """Create a new session directory and return its path."""
    base = Path(base_dir) if base_dir else LOG_DIR_DEFAULT
    session_id = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_dir = base / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


# ----------------------------------------------------------------------
# Save helpers
# ----------------------------------------------------------------------

def _write_text(file_path: Path, content: str) -> None:
    file_path.write_text(content, encoding="utf-8")


def save_raw_text(session_dir: Path, text: str) -> None:
    """Save raw ASR output."""
    _write_text(session_dir / "raw.txt", text)


def save_formatted_json(session_dir: Path, data: Dict[str, Any]) -> None:
    """Save formatted JSON output."""
    (session_dir / "formatted.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def save_prompt_text(session_dir: Path, prompt: str) -> None:
    """Save system prompt used for formatting."""
    _write_text(session_dir / "prompt.txt", prompt)


def save_meta(session_dir: Path, meta: Dict[str, Any]) -> None:
    """Save meta information as JSON."""
    (session_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    ) 
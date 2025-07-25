"""Default configuration values for Open Super Whisper GUI.

本モジュールは QSettings 未設定時に利用する既定値を提供します。
"""

from __future__ import annotations

# from pathlib import Path  # Unused; remove
from typing import Any, Dict

# Use absolute import to ensure PyInstaller compatibility
from core.logging_helper import LOG_DIR_DEFAULT

# Settings key → default value
DEFAULTS: Dict[str, Any] = {
    # ASR
    "asr/model": "whisper-1",
    # PostFormatter
    "post_formatter/enabled": True,
    "post_formatter/temperature": 0.0,
    "post_formatter/max_tokens": 0,
    "post_formatter/allow_markdown": False,
    "post_formatter/force_style": "",
    "post_formatter/system_prompt": "assets/prompts/formatter_system_prompt.txt",
    # Style guide
    "style_guide/path": "",
    # Vocabulary
    "vocabulary/list": [],
    # Log base directory
    "log/base_dir": str(LOG_DIR_DEFAULT),
}


def apply_defaults(settings) -> None:  # noqa: D401
    """Ensure that all DEFAULTS keys exist in *settings* QSettings."""
    for key, value in DEFAULTS.items():
        if settings.value(key, None) is None:
            settings.setValue(key, value) 
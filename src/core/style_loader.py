"""Style guide loader.

YAML / JSON ファイルを読み込み、辞書として返します。
ファイルが存在しない場合や `path` が空の場合は空 dict を返します。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import yaml  # type: ignore

__all__ = ["load_style"]


def load_style(path: str | Path | None) -> Dict[str, Any]:  # noqa: D401
    """Load style guide file and return as dict.

    Args:
        path: YAML / JSON file path. None or non-existent returns empty dict.

    Returns:
        dict: Style guide content; empty dict if not found.
    """
    if not path:
        return {}

    file_path = Path(path)
    if not file_path.exists():
        return {}

    ext = file_path.suffix.lower()
    try:
        if ext in {".yaml", ".yml"}:
            with file_path.open("r", encoding="utf-8") as fp:
                data = yaml.safe_load(fp) or {}
        elif ext == ".json":
            with file_path.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
        else:
            raise ValueError(f"Unsupported style guide file type: {ext}")
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Failed to load style guide: {file_path}") from exc

    if not isinstance(data, dict):
        raise RuntimeError("Style guide content must be a JSON/YAML object (dictionary).")

    return data 
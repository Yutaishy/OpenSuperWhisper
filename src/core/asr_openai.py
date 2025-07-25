"""OpenAI 音声認識クライアント (ASR)。

`openai` 新 SDK を利用して音声ファイルをテキストへ転記します。
UI から選択されたモデル ID (`whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`) を動的に切り替え可能です。
"""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Optional

from openai import OpenAI

from .interfaces.asr_base import ASRClient

__all__ = ["OpenAIASRClient"]


class OpenAIASRClient(ASRClient):
    """OpenAI 音声認識 API をラップする ASR クライアント。"""

    def __init__(self, api_key: str, model_id: str = "whisper-1", *, timeout: float | None = None) -> None:
        """Instantiate client.

        Args:
            api_key: OpenAI API キー。
            model_id: 使用する ASR モデル ID（UI から渡す）。
            timeout: 通信タイムアウト秒数。None なら SDK 既定。
        """
        self.model_id = model_id
        self._client = OpenAI(api_key=api_key, timeout=timeout)

    # ---------------------------------------------------------------------
    # ASRClient interface implementation
    # ---------------------------------------------------------------------

    def transcribe(self, audio_file: str | Path, language: Optional[str] = None) -> str:  # noqa: D401
        """音声ファイルをテキストへ転記して返す。"""
        audio_path = Path(audio_file)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            with open(audio_path, "rb") as fp:
                response = self._client.audio.transcriptions.create(
                    model=self.model_id,
                    file=fp,
                    response_format="text",
                    **({"language": language} if language else {}),
                )
        except Exception as exc:  # pylint: disable=broad-except
            # 例外を握り潰さず、意味を付与して再送出
            raise RuntimeError("OpenAI ASR transcription failed") from exc

        # 新 SDK で response_format="text" の場合は str が返る
        if isinstance(response, str):
            return response.strip()

        # 保険として .text 属性を参照
        with contextlib.suppress(AttributeError):
            return str(response.text).strip()

        # 予期せぬ形式
        return str(response).strip() 
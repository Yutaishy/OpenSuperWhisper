"""ASR 抽象インターフェース。

このクラスは音声認識エンジンをプラグイン可能にするための共通 API を定義します。
将来的に faster-whisper などへ差し替えやマルチエンジン構成を容易に行う目的で作成されています。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

__all__ = ["ASRClient"]


class ASRClient(ABC):
    """Abstract base class representing an ASR engine client."""

    @abstractmethod
    def transcribe(self, audio_file: str, language: Optional[str] = None) -> str:  # noqa: D401
        """音声ファイルをテキストへ転記して返す。

        Args:
            audio_file: 読み込む音声ファイルのパス。
            language: 音声言語 (ISO-639-1) を明示する場合に指定。

        Returns:
            認識したテキスト文字列。
        """
        raise NotImplementedError 
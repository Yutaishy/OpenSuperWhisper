"""Japanese vocabulary extractor using Janome.

音声認識結果などの自由文から「名詞」を抽出し、
出現頻度が一定以上の語を候補として返します。
既に承認済み語彙 (existing) に含まれる単語は除外します。
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Set

from janome.tokenizer import Tokenizer

__all__ = ["VocabularyExtractor"]


class VocabularyExtractor:  # pylint: disable=too-few-public-methods
    """Extract candidate nouns from Japanese text using Janome."""

    def __init__(self, *, min_freq: int = 2) -> None:  # noqa: D401
        self.min_freq = min_freq
        self._tokenizer = Tokenizer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(self, text: str, existing: Set[str] | Iterable[str] | None = None) -> List[str]:
        """Extract high-frequency nouns not already in *existing*.

        Args:
            text: 入力テキスト。
            existing: 既存語彙（承認済み）を列挙するイテラブル。

        Returns:
            条件を満たした語彙リスト（頻度降順）。
        """

        existing_set: Set[str] = set(existing) if existing else set()
        noun_counter: Counter[str] = Counter()

        for token in self._tokenizer.tokenize(text):
            pos = token.part_of_speech.split(",")[0]
            if pos != "名詞":
                continue
            surface = token.surface
            if surface in existing_set:
                continue
            # 念の為、1文字のひらがな／記号などを除外
            if len(surface) == 1:
                continue
            noun_counter[surface] += 1

        # 頻度フィルタ
        candidates = [word for word, freq in noun_counter.items() if freq >= self.min_freq]

        # 頻度降順で返す
        candidates.sort(key=lambda w: noun_counter[w], reverse=True)
        return candidates 
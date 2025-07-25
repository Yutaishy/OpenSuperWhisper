"""Post‐formatter using OpenAI Chat Completions (o4-mini).

このモジュールは ASR の生テキストを受け取り、o4-mini モデルで体裁を整形します。
整形後は JSON 形式 (`{"text": "..."}`) を強制し、`jsonschema` で検証します。
失敗時は呼び出し側でフォールバック可能な例外を送出します。
"""

from __future__ import annotations

import json
import re
from typing import Optional

from jsonschema import validate  # type: ignore
from jsonschema.exceptions import ValidationError  # type: ignore
from openai import OpenAI

__all__ = ["PostFormatter", "POST_SCHEMA"]

POST_SCHEMA = {
    "type": "object",
    "properties": {"text": {"type": "string"}},
    "required": ["text"],
    "additionalProperties": False,
}


class PostFormatter:  # pylint: disable=too-few-public-methods
    """整形を担当するクラス。"""

    def __init__(
        self,
        api_key: str,
        *,
        model: str = "o4-mini",
        temperature: float = 0.0,
        max_tokens: int | None = None,
        allow_markdown: bool = False,
        force_style: Optional[str] = None,
        force_json: bool = True,
        system_prompt_base: str | None = None,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.allow_markdown = allow_markdown
        self.force_style = force_style  # "desu" / "da" / None
        self.force_json = force_json
        self._client = OpenAI(api_key=api_key)
        self._base_system_prompt = system_prompt_base or (
            "あなたはプロの日本語編集者です。入力テキストを読みやすい文章に整形してください。"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def format(self, raw_text: str, style_guide: Optional[dict] = None) -> str:  # noqa: D401
        """生テキストを整形し、整形後テキストを返す。"""
        system_prompt = self._build_system_prompt(style_guide)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text},
        ]

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=messages,
            )
        except Exception as exc:  # pylint: disable=broad-except
            raise RuntimeError("PostFormatter: OpenAI API call failed") from exc

        # Assume new SDK -> response.choices[0].message.content (str)
        try:
            content = response.choices[0].message.content  # type: ignore[attr-defined]
        except Exception as exc:  # pylint: disable=broad-except
            raise RuntimeError("PostFormatter: unexpected API response format") from exc

        formatted_text = self._parse_and_validate(content)
        return formatted_text

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _build_system_prompt(self, style_guide: Optional[dict]) -> str:
        parts: list[str] = [self._base_system_prompt]
        if not self.allow_markdown:
            parts.append("Markdownの構造を作るな。Plain text とし、箇条書きもハイフンを使用せず1文ずつ改行すること。")

        style = self.force_style or self.detect_style(None)
        if style == "desu":
            parts.append("文体は「です・ます」調で統一せよ。")
        elif style == "da":
            parts.append("文体は「だ・である」調で統一せよ。")

        if self.force_json:
            parts.append(
                "出力は必ず次の JSON 形式のみで返す: {\"text\": \"整形済みテキスト\"}。"
                "文字列以外を含めるな。"
            )

        if style_guide:
            # シンプルに連結
            parts.append("スタイルガイドを順守せよ:\n" + json.dumps(style_guide, ensure_ascii=False))

        return "\n".join(parts)

    @staticmethod
    def detect_style(text: Optional[str]) -> str:
        """簡易的に文体を推定する (`desu` / `da`)。"""
        if not text:
            return "desu"  # デフォルト

        desu_count = len(re.findall(r"です|ます", text))
        da_count = len(re.findall(r"だ。|である", text))
        return "desu" if desu_count >= da_count else "da"

    def _parse_and_validate(self, content: str) -> str:
        """モデル応答を JSON としてパース & 検証し、text を返す。"""
        data: dict[str, object]
        # まず JSON として読み取る
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # JSON で返っていなければフォールバック
            data = {"text": content.strip()}

        # 検証
        try:
            validate(data, POST_SCHEMA)
        except ValidationError as exc:
            raise RuntimeError("PostFormatter: JSON schema validation failed") from exc

        return str(data["text"]) 
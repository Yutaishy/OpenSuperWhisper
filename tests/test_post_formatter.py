import pytest

from src.core.post_formatter import PostFormatter


def test_parse_valid_json():
    pf = PostFormatter(api_key="dummy")
    result = pf._parse_and_validate('{"text": "Hello"}')  # type: ignore[attr-defined]
    assert result == "Hello"


def test_parse_invalid_json_fallback():
    pf = PostFormatter(api_key="dummy")
    result = pf._parse_and_validate("plain text")  # type: ignore[attr-defined]
    assert result == "plain text"


def test_style_detection_desu_da():
    assert PostFormatter.detect_style("これはテストです。よろしくお願いします。") == "desu"
    assert PostFormatter.detect_style("これはテストだ。よろしくである。") == "da" 
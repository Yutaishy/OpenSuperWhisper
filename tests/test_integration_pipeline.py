import os
import pytest

from src.core.post_formatter import PostFormatter


@pytest.mark.skipif(os.getenv("RUN_REAL_API_TEST") != "1", reason="Requires RUN_REAL_API_TEST=1")
def test_post_formatter_real_api():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")
    pf = PostFormatter(api_key=api_key)
    result = pf.format("こんにちは。テストです。", style_guide=None)
    assert isinstance(result, str) and len(result) > 0 
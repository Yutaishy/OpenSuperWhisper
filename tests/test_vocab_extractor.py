from src.core.vocab_extractor import VocabularyExtractor


def test_vocab_extractor_frequency():
    text = "Pythonはプログラミング言語です。Pythonは人気です。AIとPython。"
    extractor = VocabularyExtractor(min_freq=2)
    result = extractor.extract(text, existing=set())
    assert "Python" in result
    assert "AI" not in result


def test_vocab_extractor_existing_exclusion():
    text = "モデル モデル モデル テスト"
    extractor = VocabularyExtractor(min_freq=2)
    result = extractor.extract(text, existing={"モデル"})
    assert "モデル" not in result 
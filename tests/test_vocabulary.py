import OpenSuperWhisper.vocabulary as vocab

def test_extract_new_vocabulary_basic():
    text = "これはテストです。東京に行きました。"
    known = {"テスト"}
    new_words = vocab.extract_new_vocabulary(text, known)
    assert "東京" in new_words
    assert "テスト" not in new_words

def test_user_dictionary_save_load(tmp_path):
    words = {"apple", "orange"}
    dict_file = tmp_path / "dict.txt"
    vocab.save_user_dictionary(str(dict_file), words)
    loaded = vocab.load_user_dictionary(str(dict_file))
    assert words == loaded

def test_user_dictionary_nonexistent_file():
    loaded = vocab.load_user_dictionary("nonexistent.txt")
    assert loaded == set()
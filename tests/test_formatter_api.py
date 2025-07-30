import OpenSuperWhisper.formatter_api as fmt


class MockMessage:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockChatResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

def test_format_text_monkeypatch(monkeypatch):
    def mock_create(**kwargs):
        return MockChatResponse("Formatted Output")

    def mock_get_client():
        class MockClient:
            def __init__(self):
                self.chat = type('', (), {})()
                self.chat.completions = type('', (), {})()
                self.chat.completions.create = mock_create
        return MockClient()

    monkeypatch.setattr(fmt, "get_client", mock_get_client)

    raw = "raw text"
    prompt = "Make it fancy."
    style = "No slang."
    result = fmt.format_text(raw, prompt, style_guide=style, model="gpt-4o-mini")
    assert result == "Formatted Output"

def test_format_text_o4_mini_high(monkeypatch):
    def mock_create(**kwargs):
        # Verify temperature=0.0 is set for o4-mini-high
        assert kwargs.get("temperature") == 0.0
        return MockChatResponse("Formatted with o4-mini-high")

    def mock_get_client():
        class MockClient:
            def __init__(self):
                self.chat = type('', (), {})()
                self.chat.completions = type('', (), {})()
                self.chat.completions.create = mock_create
        return MockClient()

    monkeypatch.setattr(fmt, "get_client", mock_get_client)

    raw = "test input"
    prompt = "Format professionally."
    result = fmt.format_text(raw, prompt, model="o4-mini-high")
    assert result == "Formatted with o4-mini-high"

def test_format_text_exception(monkeypatch):
    def mock_create(**kwargs):
        raise Exception("API Error")

    def mock_get_client():
        class MockClient:
            def __init__(self):
                self.chat = type('', (), {})()
                self.chat.completions = type('', (), {})()
                self.chat.completions.create = mock_create
        return MockClient()

    monkeypatch.setattr(fmt, "get_client", mock_get_client)

    try:
        fmt.format_text("raw text", "prompt")
        raise AssertionError("Should have raised exception")
    except Exception as e:
        assert "Formatting API call failed" in str(e)

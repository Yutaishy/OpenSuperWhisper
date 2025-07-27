import OpenSuperWhisper.asr_api as asr
import OpenSuperWhisper.formatter_api as fmt
import OpenSuperWhisper.vocabulary as vocab


class MockTranscriptionResponse:
    def strip(self):
        return "これはテストです。"

class MockMessage:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockChatResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

def test_full_pipeline_integration(monkeypatch, tmp_path):
    # Create dummy audio file
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"RIFF....")

    # Mock ASR response
    def mock_transcribe(*args, **kwargs):
        return MockTranscriptionResponse()

    def mock_get_asr_client():
        class MockClient:
            def __init__(self):
                self.audio = type('', (), {})()
                self.audio.transcriptions = type('', (), {})()
                self.audio.transcriptions.create = mock_transcribe
        return MockClient()

    monkeypatch.setattr(asr, "get_client", mock_get_asr_client)

    # Mock formatter response
    def mock_chat_create(**kwargs):
        return MockChatResponse("This is a test.")

    def mock_get_fmt_client():
        class MockClient:
            def __init__(self):
                self.chat = type('', (), {})()
                self.chat.completions = type('', (), {})()
                self.chat.completions.create = mock_chat_create
        return MockClient()

    monkeypatch.setattr(fmt, "get_client", mock_get_fmt_client)

    # Test the pipeline
    raw_text = asr.transcribe_audio(str(audio_file), model="whisper-1")
    assert raw_text == "これはテストです。"

    # Test vocabulary extraction
    known_words = set()
    new_words = vocab.extract_new_vocabulary(raw_text, known_words)
    assert "テスト" in new_words

    # Test formatting
    formatted = fmt.format_text(raw_text, "Format properly", model="gpt-4o-mini")
    assert formatted == "This is a test."

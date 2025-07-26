import OpenSuperWhisper.asr_api as asr

class MockTranscriptionResponse:
    def strip(self):
        return "Hello world."

def test_transcribe_audio_monkeypatch(monkeypatch, tmp_path):
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"RIFF....")
    
    def mock_create(*args, **kwargs):
        return MockTranscriptionResponse()
    
    def mock_get_client():
        class MockClient:
            def __init__(self):
                self.audio = type('', (), {})()
                self.audio.transcriptions = type('', (), {})()
                self.audio.transcriptions.create = mock_create
        return MockClient()
    
    monkeypatch.setattr(asr, "get_client", mock_get_client)
    result = asr.transcribe_audio(str(audio_file), model="whisper-1")
    assert result == "Hello world."

def test_transcribe_audio_exception(monkeypatch, tmp_path):
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"RIFF....")
    
    def mock_create(*args, **kwargs):
        raise Exception("API Error")
    
    def mock_get_client():
        class MockClient:
            def __init__(self):
                self.audio = type('', (), {})()
                self.audio.transcriptions = type('', (), {})()
                self.audio.transcriptions.create = mock_create
        return MockClient()
    
    monkeypatch.setattr(asr, "get_client", mock_get_client)
    
    try:
        asr.transcribe_audio(str(audio_file), model="whisper-1")
        assert False, "Should have raised exception"
    except Exception as e:
        assert "ASR transcription failed" in str(e)
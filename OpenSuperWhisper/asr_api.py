
import os

from openai import OpenAI

client = None

def get_client() -> OpenAI:
    global client
    if client is None:
        # Set shorter timeouts for CI environments
        timeout = 60.0 if os.getenv('CI') else 120.0
        client = OpenAI(timeout=timeout)
    return client

def transcribe_audio(audio_path: str, model: str = "whisper-1") -> str:
    """
    Transcribe the given audio file using OpenAI's ASR API.
    :param audio_path: Path to an audio file (wav, mp3, etc.)
    :param model: ASR model to use (e.g., 'whisper-1', 'gpt-4o-transcribe', 'gpt-4o-mini-transcribe')
    :return: Transcribed text as a string.
    :raises: Exception if transcription fails.
    """
    with open(audio_path, "rb") as audio_file:
        try:
            client = get_client()
            transcript = client.audio.transcriptions.create(
                file=audio_file,
                model=model,
                response_format="text"
            )
        except Exception as e:
            raise Exception(f"ASR transcription failed: {e}") from e
    return transcript.strip()

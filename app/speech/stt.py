import base64
from typing import Optional


class SpeechToText:
    def transcribe(self, audio_bytes: bytes) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class DummySTT(SpeechToText):
    def transcribe(self, audio_bytes: bytes) -> str:
        return ""


class WhisperSTT(SpeechToText):
    """
    Optional offline STT using OpenAI Whisper. Requires the `openai-whisper` package
    and an available audio backend.
    """

    def __init__(self, model_name: str = "base"):
        try:
            import whisper  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Whisper is not installed. Install openai-whisper to enable STT."
            ) from exc
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_bytes: bytes) -> str:
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            result = self.model.transcribe(tmp.name)
        return result.get("text", "").strip()


def decode_audio(audio_base64: Optional[str]) -> bytes:
    if not audio_base64:
        return b""
    return base64.b64decode(audio_base64)

import base64
import io
from typing import Optional


class TextToSpeech:
    def synthesize(self, text: str) -> bytes:  # pragma: no cover - interface
        raise NotImplementedError


class Pyttsx3TTS(TextToSpeech):
    """
    Offline-friendly TTS using pyttsx3. Falls back to raw bytes if the engine
    cannot write audio (useful for CI or headless environments).
    """

    def __init__(self):
        try:
            import pyttsx3  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("pyttsx3 is required for TTS.") from exc
        self.engine = pyttsx3.init()

    def synthesize(self, text: str) -> bytes:
        import tempfile

        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
                self.engine.save_to_file(text, tmp.name)
                self.engine.runAndWait()
                tmp.seek(0)
                return tmp.read()
        except Exception:
            return text.encode("utf-8")


class NullTTS(TextToSpeech):
    def synthesize(self, text: str) -> bytes:
        return text.encode("utf-8")


def encode_audio(audio_bytes: Optional[bytes]) -> Optional[str]:
    if not audio_bytes:
        return None
    return base64.b64encode(audio_bytes).decode("utf-8")

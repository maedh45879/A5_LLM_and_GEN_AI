from app.config import Settings
from app.speech.stt import DummySTT, SpeechToText, WhisperSTT
from app.speech.tts import NullTTS, Pyttsx3TTS, TextToSpeech


def build_stt(settings: Settings) -> SpeechToText:
    provider = settings.speech.stt_provider.lower()
    if provider == "whisper":
        return WhisperSTT()
    return DummySTT()


def build_tts(settings: Settings) -> TextToSpeech:
    provider = settings.speech.tts_provider.lower()
    if provider == "pyttsx3":
        try:
            return Pyttsx3TTS()
        except Exception:
            return NullTTS()
    return NullTTS()

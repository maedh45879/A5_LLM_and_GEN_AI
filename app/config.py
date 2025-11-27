from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseModel):
    model_config = SettingsConfigDict(populate_by_name=True)

    provider: str = Field(
        default="ollama",
        description="LLM provider identifier, e.g. 'ollama' or 'google'",
        alias="LLM_PROVIDER",
    )
    model: str = Field(
        default="llama3",
        description="Model name for the selected provider",
        alias="LLM_MODEL",
    )
    temperature: float = Field(default=0.2, ge=0.0, le=1.0, alias="LLM_TEMPERATURE")
    max_tokens: int = Field(default=512, ge=64, le=4096, alias="LLM_MAX_TOKENS")


class SpeechSettings(BaseModel):
    model_config = SettingsConfigDict(populate_by_name=True)

    stt_provider: str = Field(default="dummy", alias="SPEECH_STT_PROVIDER")
    tts_provider: str = Field(default="pyttsx3", alias="SPEECH_TTS_PROVIDER")
    sample_rate: int = Field(default=16000, alias="SPEECH_SAMPLE_RATE")


class RAGSettings(BaseModel):
    model_config = SettingsConfigDict(populate_by_name=True)

    menu_dir: Path = Field(default=Path("data/menu"), alias="RAG_MENU_DIR")
    vector_store_path: Path = Field(
        default=Path("data/vector_store"), alias="RAG_VECTOR_STORE_PATH"
    )
    chunk_size: int = Field(default=750, alias="RAG_CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, alias="RAG_CHUNK_OVERLAP")


class APISettings(BaseModel):
    host: str = Field(default="0.0.0.0", alias="API_HOST")
    port: int = Field(default=8000, alias="API_PORT")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        env_nested_delimiter="__",
        populate_by_name=True,
        extra="allow",
    )

    project_name: str = "Voice-Enabled GenAI Restaurant Assistant"
    environment: str = "development"

    llm: LLMSettings = LLMSettings()
    speech: SpeechSettings = SpeechSettings()
    rag: RAGSettings = RAGSettings()
    api: APISettings = APISettings()

    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    google_project_id: Optional[str] = Field(default=None, alias="GOOGLE_PROJECT_ID")
    google_location: Optional[str] = Field(default=None, alias="GOOGLE_LOCATION")


@lru_cache()
def get_settings() -> Settings:
    return Settings()

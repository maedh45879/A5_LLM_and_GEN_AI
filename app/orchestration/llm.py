from typing import Any

from langchain.schema.language_model import BaseLanguageModel

from app.config import Settings


def get_chat_model(settings: Settings) -> BaseLanguageModel:
    """
    Build a chat model client based on settings.

    Providers:
    - ollama: local models via Ollama daemon.
    - google: Gemini via Google Generative AI.
    Fallback: simple stub model for tests/dev.
    """
    provider = settings.llm.provider.lower()
    model_name = settings.llm.model
    common_kwargs: dict[str, Any] = {
        "temperature": settings.llm.temperature,
        "max_tokens": settings.llm.max_tokens,
    }

    if provider == "ollama":
        try:
            from langchain_community.chat_models import ChatOllama
        except Exception as exc:  # pragma: no cover - import guard
            raise RuntimeError(
                "ChatOllama is not available. Install langchain-community."
            ) from exc

        return ChatOllama(model=model_name, **common_kwargs)

    if provider == "google":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except Exception as exc:  # pragma: no cover - import guard
            raise RuntimeError(
                "ChatGoogleGenerativeAI not available. Install langchain-google-genai."
            ) from exc

        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.google_api_key,
            convert_system_message_to_human=True,
            **common_kwargs,
        )

    # Lightweight stub for tests or unsupported providers
    try:
        from langchain.chat_models.fake import FakeListChatModel
        from langchain.schema import AIMessage
    except Exception:
        raise RuntimeError("LangChain is required for the fallback stub model.")

    return FakeListChatModel(
        responses=[AIMessage(content="Hello from the fallback assistant.")],
        **common_kwargs,
    )

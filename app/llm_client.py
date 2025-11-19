import os
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


SYSTEM_PROMPT = """
You are a helpful, polite restaurant receptionist.
You can:
- take table reservations (name, date, time, number of guests),
- take takeaway/delivery orders,
- answer questions about the menu,
- answer general questions (location, opening hours, etc.).
Ask clarifying questions if needed and keep answers short and clear.
"""


async def generate_reply(user_message: str, history: list[dict] | None = None) -> str:
    """
    Call a local Ollama chat model and return the assistant reply.
    history is a list of {"role": "user"|"assistant", "content": "..."}.
    """
    if history is None:
        history = []

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()
        # Ollama chat API format: data["message"]["content"]
        return data["message"]["content"]

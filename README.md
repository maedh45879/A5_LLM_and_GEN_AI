# Voice-Enabled GenAI Restaurant Assistant

Offline-first restaurant assistant that handles voice or text for reservations, orders, menu Q&A (RAG), and general info. Works with local Ollama models or Google Gemini.

## Features
- FastAPI backend with endpoints for voice, reservations, orders, menu QA, and general info.
- Configurable LLM provider: Ollama (`llama3`, `mistral`, etc.) or Google Generative AI (Gemini/Vertex).
- RAG over local menu/FAQ docs using Chroma + sentence transformers.
- Pluggable speech layer (STT/TTS) with offline-friendly defaults (pyttsx3, optional Whisper).
- Streamlit UI with chat/voice loop, TTS playback, reservation/order/menu widgets (mobile-friendly layout).
- Minimal tests for health and intent routing; Docker & docker-compose for API + UI.

## Architecture
- **FastAPI (`app/api.py`)**: routes + dependency wiring; voice endpoint orchestrates STT → intent router → tools/LLM → TTS.
- **Orchestration (`app/orchestration/`)**: intent router, LLM factory, agents for reservations/orders/general, menu QA tool (RAG).
- **RAG (`app/rag/`)**: ingest script -> Chroma vector store; retriever loaded at runtime.
- **Speech (`app/speech/`)**: abstractions + providers (dummy, Whisper STT; pyttsx3/Null TTS).
- **UI (`ui/streamlit_app.py`)**: chat/voice pane, reservation/order forms, menu QA card.
- **Config (`app/config.py`)**: Pydantic settings with `.env` support.

## Setup
1. **Prereqs**
   - Python 3.11+
   - [Ollama](https://ollama.com/download) running locally for offline LLMs (e.g., `ollama run llama3` to pull the model), or Google API key for online mode.
   - Optional: FFmpeg + audio device if you need full STT/TTS.
2. **Install deps**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate     # on Windows
   cd A5_LLM_AND_GEN_AI
   pip install -r requirements.txt
   # Optional (for Whisper STT): pip install "git+https://github.com/openai/whisper.git"
   ```
3. **Environment**
   - Copy `.env.example` to `.env` and adjust:
     - `LLM_PROVIDER=ollama|google`
     - `LLM_MODEL=llama3` (Ollama) or `gemini-1.5-flash` (Google)
     - `GOOGLE_API_KEY` (if using Google)
     - `RAG_*` paths, `BACKEND_URL` for UI.

## Run the backend
```bash
python main.py  # starts FastAPI on host/port from config (default 0.0.0.0:8000)
```
Endpoints of interest:
- `GET /health`
- `POST /voice` (`audio_base64` or `text`)
- `POST /reservation`, `/order`, `/menu/qa`, `/info`

## Build the menu knowledge base (RAG)
1. Add/update docs under `data/menu/` (`.txt`, `.md`, `.pdf`).
2. Run ingestion (creates `data/vector_store/`):
   ```bash
   python scripts/ingest_menu.py
   ```

## Run the Streamlit UI
```bash
export BACKEND_URL=http://localhost:8000  # or set in .env
streamlit run ui/streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```
- Chat pane accepts text or audio upload; responses include TTS playback when available.
- Reservation/order/menu widgets call the backend endpoints directly.

## Docker (optional)
Build and run API+UI:
```bash
docker compose up --build
```
Services:
- `api`: `uvicorn app.api:app` on `8000`
- `ui`: `streamlit_app.py` on `8501` (uses `BACKEND_URL=http://api:8000`)
The `data/` directory is mounted for vector store persistence.

## Configuration reference
- See `.env.example` and `app/config.py` for all options.
- Speech:
  - `SPEECH_STT_PROVIDER`: `dummy` (default) or `whisper` (install Whisper separately).
  - `SPEECH_TTS_PROVIDER`: `pyttsx3` (offline) or `null`.
- LLM:
  - Ollama: ensure the daemon is running and the model is pulled.
  - Google: set `GOOGLE_API_KEY`, optionally project/location for Vertex.

## Testing
```bash
pytest
```
Includes health check and intent routing coverage. Voice/LLM paths are structured for easy mocking.

## Troubleshooting
- **LLM unavailable**: the app logs the error and continues; responses fall back to static messages. Verify `LLM_PROVIDER` and that Ollama/Google creds are available.
- **RAG not initialized**: run `python scripts/ingest_menu.py` after adding docs.
- **TTS/STT issues**: switch to `dummy/null` providers in `.env` to bypass audio during CI or headless use.
- **Model downloads**: the embedding model (`sentence-transformers/all-MiniLM-L6-v2`) downloads on first run; pre-download in connected environments if running fully offline.

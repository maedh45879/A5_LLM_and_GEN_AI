# 🍽️ Voice-Enabled GenAI Restaurant Assistant (MVP)

> **AI-powered receptionist for restaurants** — built with **FastAPI + Ollama**.
> This MVP provides a text-based conversational assistant able to take reservations, answer menu questions, and simulate customer interactions.
> Voice interactions, RAG (menu info), and multi-agent orchestration will be added in later versions.

---

## 🚀 Features (Current MVP)

✔ Conversational restaurant assistant
✔ Takes reservations through natural language
✔ Answers menu + general questions
✔ Runs locally with **Ollama** (free, open-source models)
✔ Simple API endpoint (`/api/chat`)
✔ Reproducible and documented

> 💡 Next steps (future updates): Voice, RAG, Multi-Agents, Streamlit UI

---

## 🏗️ Tech Stack

| Component          | Technology                  |
| ------------------ | --------------------------- |
| Backend            | FastAPI                     |
| LLM Inference      | Ollama (default: `mistral`) |
| HTTP Requests      | httpx                       |
| Deployment (later) | Docker                      |
| UI (later)         | Streamlit                   |

---

## 📂 Project Structure

```
genai-restaurant-assistant/
│
├── app/
│   ├── __init__.py
│   ├── llm_client.py      # LLM call wrapper for Ollama
│   └── api.py             # FastAPI REST endpoints
│
├── main.py                # FastAPI entrypoint
├── requirements.txt
└── README.md
```

---

## 🔧 Installation

### ⚙️ 1️⃣ Create and activate a virtual environment

#### 🖥️ Mac / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 🪟 Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\activate
```

> 💡 Always activate the venv **before running or installing anything**.

---

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Install Ollama (if not installed)

[https://ollama.com/download](https://ollama.com/download)

Then pull a model (ex: Mistral)

```bash
ollama pull mistral
```

---

## ▶️ Run the Application

Start FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at:

```
http://localhost:8000/api/chat
```

---

## 📡 Example API Call

### Using `curl`

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
        "message": "I want to book a table for 4 tonight at 8pm",
        "history": []
      }'
```

### Example Response

```json
{
  "reply": "Sure! Can I have your name for the reservation?"
}
```

---

## 📝 License

This project uses open-source, academic-friendly LLMs and tools.
You are free to use, modify, and distribute under **MIT License**.

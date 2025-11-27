import base64
import json
import os
from datetime import date, time

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
st.set_page_config(page_title="GenAI Restaurant Assistant", layout="wide")


def call_api(path: str, payload: dict):
    url = f"{BACKEND_URL}{path}"
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def render_audio(audio_base64: str):
    if not audio_base64:
        return
    audio_bytes = base64.b64decode(audio_base64)
    st.audio(audio_bytes, format="audio/wav")


st.title("Voice-Enabled GenAI Restaurant Assistant")
st.caption("Works with Ollama (offline) or Google AI (online).")

col_voice, col_side = st.columns([3, 2], gap="large")

with col_voice:
    st.subheader("Voice / Chat")
    st.write("Type a message or upload audio to see the assistant respond with speech.")
    text_input = st.text_area("Your message", placeholder="Ask about the menu or book a table...")
    audio_file = st.file_uploader("Upload audio (wav)", type=["wav"])

    if "history" not in st.session_state:
        st.session_state.history = []

    if st.button("Send", use_container_width=True):
        audio_b64 = None
        if audio_file:
            audio_b64 = base64.b64encode(audio_file.read()).decode("utf-8")
        payload = {"text": text_input, "audio_base64": audio_b64}
        try:
            data = call_api("/voice", payload)
            st.session_state.history.append(
                {"user": text_input or "voice message", "assistant": data["text"]}
            )
            st.success(f"Intent: {data.get('intent')}")
            st.write(data["text"])
            render_audio(data.get("audio_base64"))
        except Exception as exc:
            st.error(f"Voice request failed: {exc}")

    st.divider()
    st.subheader("Chat History")
    for turn in st.session_state.history[::-1]:
        st.markdown(f"**You:** {turn['user']}")
        st.markdown(f"**Assistant:** {turn['assistant']}")
        st.markdown("---")

with col_side:
    st.subheader("Reservations")
    with st.form("reservation_form"):
        name = st.text_input("Name")
        res_date = st.date_input("Date", value=date.today())
        res_time = st.time_input("Time", value=time(19, 0))
        guests = st.number_input("Guests", min_value=1, max_value=12, value=2)
        notes = st.text_input("Special requests", value="")
        submit_res = st.form_submit_button("Book")
    if submit_res:
        payload = {
            "name": name,
            "date": res_date.isoformat(),
            "time": res_time.strftime("%H:%M"),
            "guests": int(guests),
            "special_requests": notes or None,
        }
        try:
            data = call_api("/reservation", payload)
            st.success(data["message"])
        except Exception as exc:
            st.error(f"Reservation failed: {exc}")

    st.subheader("Place an Order")
    with st.form("order_form"):
        order_text = st.text_area("Items (e.g., 2x Margherita, 1x Tiramisu)")
        table = st.text_input("Table (optional)")
        submit_order = st.form_submit_button("Send Order")
    if submit_order:
        # simple parsing: split by comma
        items = []
        for raw in order_text.split(","):
            item = raw.strip()
            if not item:
                continue
            qty = 1
            if "x" in item[:4]:
                parts = item.split("x", 1)
                try:
                    qty = int(parts[0].strip())
                    item = parts[1].strip()
                except Exception:
                    qty = 1
            items.append({"item": item, "quantity": qty})
        payload = {"table": table or None, "items": items}
        try:
            data = call_api("/order", payload)
            st.success(data["message"])
        except Exception as exc:
            st.error(f"Order failed: {exc}")

    st.subheader("Menu Q&A")
    question = st.text_input("Ask about ingredients, allergens, promos")
    if st.button("Ask", use_container_width=True):
        try:
            data = call_api("/menu/qa", {"question": question})
            st.write(data["answer"])
            if data.get("sources"):
                st.caption(f"Sources: {', '.join(data['sources'])}")
        except Exception as exc:
            st.error(f"Menu QA failed: {exc}")

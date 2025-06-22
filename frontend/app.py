import sys
import os
import streamlit as st
import requests
import uuid
import random
from io import BytesIO
from PIL import Image

# Ensure 'frontend' is importable when running from neuro_rag
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sidebar import sidebar
from utils import render_sources, render_grounding_score, render_latency

API_URL = "http://localhost:8000"

# Set pitch black theme and custom CSS
st.set_page_config(page_title="NeuroRAG Chatbot", layout="wide")
custom_css = """
<style>
body, .stApp, .css-18e3th9, .css-1d391kg, .css-1v0mbdj, .css-1dp5vir, .css-1c7y2kd, .css-1v4eu6x {
    background-color: #111 !important;
    color: #fff !important;
}
.stChatBubble {
    border-radius: 18px;
    padding: 12px 18px;
    margin: 8px 0;
    max-width: 70%;
    font-size: 1.1em;
}
.stUserBubble {
    background: #222;
    color: #fff;
    margin-left: auto;
    text-align: right;
}
.stAIBubble {
    background: #23272f;
    color: #fff;
    margin-right: auto;
    text-align: left;
}
.stSidebar {
    background: #000 !important;
    color: #fff !important;
}
.stFileUpload {
    margin-top: 12px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Sidebar: session history and chats
with st.sidebar:
    st.markdown("<div class='stSidebar'>", unsafe_allow_html=True)
    sidebar()
    st.markdown("</div>", unsafe_allow_html=True)

# Session ID
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

# Chat history
if "history" not in st.session_state:
    st.session_state["history"] = []

st.markdown("""
    <h1 style='color:#fff; text-align:center; margin-bottom:0;'>🧠 NeuroRAG Chatbot</h1>
    <hr style='border:1px solid #333; margin-bottom:0;'>
""", unsafe_allow_html=True)

# Main chat window
chat_col, upload_col = st.columns([4, 1], gap="large")

with chat_col:
    chat_box = st.container()
    with chat_box:
        for msg in st.session_state["history"]:
            if msg["role"] == "user":
                st.markdown(f"<div class='stChatBubble stUserBubble'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='stChatBubble stAIBubble'>{msg['content']}</div>", unsafe_allow_html=True)
                render_sources(msg.get("sources", []))
                render_grounding_score(msg.get("grounding_score", 0.0))
                render_latency(msg.get("latency", ""))

    # Chat input
    if "input_key" not in st.session_state:
        st.session_state["input_key"] = str(random.randint(0, 1_000_000))
    user_input = st.text_input("Type your message or paste a URL...", key=st.session_state["input_key"])
    send = st.button("Send", key="send_btn")

    # Auto-detect URL in user input
    import re
    url_pattern = re.compile(r"https?://[\w\.-/]+")
    detected_url = url_pattern.search(user_input.strip()) if user_input else None
    if detected_url:
        url = detected_url.group(0)
        with st.spinner("Uploading and indexing URL..."):
            try:
                resp = requests.post(f"{API_URL}/upload", data={"url": url})
                if resp.ok:
                    st.success("URL ingested and indexed!")
                else:
                    st.error(f"Failed to ingest URL: {resp.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
        st.session_state["input_key"] = str(random.randint(0, 1_000_000))
        st.rerun()

    if send and user_input:
        # Add user message to history
        st.session_state["history"].append({"role": "user", "content": user_input})
        with st.spinner("Getting answer from backend..."):
            try:
                payload = {"query": user_input, "session_id": st.session_state["session_id"]}
                resp = requests.post(f"{API_URL}/chat", json=payload)
                if resp.ok:
                    data = resp.json()
                    st.session_state["history"].append({
                        "role": "ai",
                        "content": data["answer"],
                        "sources": data["sources"],
                        "grounding_score": data["grounding_score"],
                        "latency": data["latency"]
                    })
                else:
                    st.session_state["history"].append({"role": "ai", "content": f"Error: {resp.text}"})
            except Exception as e:
                st.session_state["history"].append({"role": "ai", "content": f"Error: {e}"})
        st.session_state["input_key"] = str(random.randint(0, 1_000_000))
        st.rerun()

with upload_col:
    st.markdown("<div class='stFileUpload'>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload documents", type=["pdf", "csv", "txt", "docx", "md"], accept_multiple_files=True)
    if uploaded_files:
        files = [(f.name, f) for f in uploaded_files]
        files_payload = [("files", (f[0], f[1], "application/octet-stream")) for f in files]
        with st.spinner("Uploading documents..."):
            try:
                resp = requests.post(f"{API_URL}/upload", files=files_payload)
                if resp.ok:
                    st.success("Files uploaded and indexed!")
                else:
                    st.error("Upload failed.")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
    st.markdown("</div>", unsafe_allow_html=True) 
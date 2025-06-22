import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def sidebar():
    st.sidebar.title("📁 Sessions & Upload")
    # Session history
    resp = requests.get(f"{API_URL}/sessions")
    if resp.ok:
        sessions = resp.json().get("sessions", [])
        st.sidebar.markdown("**Past Sessions:**")
        for sid in sessions:
            st.sidebar.write(sid)
    # File upload
    uploaded_files = st.sidebar.file_uploader("Upload documents", type=["pdf", "csv", "txt", "docx", "md"], accept_multiple_files=True)
    if uploaded_files:
        files = [(f.name, f) for f in uploaded_files]
        files_payload = [("files", (f[0], f[1], "application/octet-stream")) for f in files]
        resp = requests.post(f"{API_URL}/upload", files=files_payload)
        if resp.ok:
            st.sidebar.success("Files uploaded and indexed!")
        else:
            st.sidebar.error("Upload failed.")
    # URL input
    url = st.sidebar.text_input("Paste a web URL to ingest")
    if url and st.sidebar.button("Ingest URL"):
        resp = requests.post(f"{API_URL}/upload", data={"url": url})
        if resp.ok:
            st.sidebar.success("URL ingested and indexed!")
        else:
            st.sidebar.error("Failed to ingest URL.")
    # Reset
    if st.sidebar.button("Reset All (Clear Memory & Index)"):
        resp = requests.post(f"{API_URL}/reset")
        if resp.ok:
            st.sidebar.success("System reset!")
            st.session_state.clear()
        else:
            st.sidebar.error("Reset failed.") 
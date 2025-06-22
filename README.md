# NeuroRAG: Advanced Local RAG Chatbot

## Overview
A fully local, production-grade, grounded RAG-based chatbot with advanced retrieval, source attribution, and explainability. Supports PDF, CSV, TXT, DOCX, Markdown, and web URLs. Powered by FastAPI, Streamlit, LangChain, Gemini, and FAISS.

## Features
- Advanced RAG: LLM-based cleaning, semantic chunking, HyQI, HyDE, self-query, CRAG, reranking, chain-of-thought, self-RAG, grounding, source attribution
- File & URL ingestion (PDF, CSV, TXT, DOCX, MD, web)
- ChatGPT-style UI (Streamlit)
- Session memory, history, reset
- Grounding score, latency, and source highlighting
- Local-first, Docker deployable

## Setup
1. Clone repo and `cd neuro_rag`
2. Create `.env`:
   ```ini
   GEMINI_API_KEY=your_key
   CHUNK_SIZE=512
   OVERLAP=50
   TOP_K=4
   TEMPERATURE=0.4
   GROUNDING_THRESHOLD=0.75
   RETRIEVAL_MODE=semantic
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run backend:
   ```bash
   uvicorn backend.main:app --reload
   ```
5. Run frontend:
   ```bash
   streamlit run frontend/app.py
   ```

## Docker
Build and run all-in-one:
```bash
docker build -t neurorag .
docker run -p 8000:8000 -p 8501:8501 --env-file .env neurorag
```

## API Endpoints
- `POST /upload`: Upload files or URLs for ingestion
- `POST /chat`: `{ query, session_id }` → `{ answer, sources, grounding_score, history, latency }`
- `GET /sessions`: List session IDs
- `POST /reset`: Clear FAISS index and memory

## Notes
- No authentication (local-first)
- For advanced features (GraphRAG, reranker), see TODOs in code
- Extendable for metadata filtering, new data types, and more

---
MIT License 
from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
from backend.loaders import load_document, load_url
from backend.vector_store import vector_store_manager
from backend.memory import memory_manager
from backend.rag_chain import rag_chain

router = APIRouter()

UPLOAD_DIR = "data/uploaded_docs/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload(files: Optional[List[UploadFile]] = File(None), url: Optional[str] = Form(None)):
    docs = []
    if files:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            docs.extend(load_document(file_path))
    if url:
        docs.extend(load_url(url))
    # Preprocess and chunk (stub: just use docs as is)
    # TODO: Use rag_chain.preprocess and rag_chain.semantic_chunk
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]
    vector_store_manager.add_texts(texts, metadatas)
    return {"status": "uploaded", "num_docs": len(docs)}

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    query = data.get("query")
    session_id = data.get("session_id")
    if not query or not session_id:
        return JSONResponse(status_code=400, content={"error": "Missing query or session_id"})
    result = rag_chain.run_chat(query, session_id)
    return result

@router.get("/sessions")
async def list_sessions():
    sessions = memory_manager.list_sessions()
    return {"sessions": sessions}

@router.post("/reset")
async def reset():
    vector_store_manager.reset()
    # Clear all session memories
    memory_manager.memories.clear()
    return {"status": "reset"} 
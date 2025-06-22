from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def calculate_grounding_score(answer: str, sources: List[Dict]) -> float:
    if not sources:
        return 0.0
    answer_emb = np.array(embeddings.embed_query(answer)).reshape(1, -1)
    chunk_embs = np.array([embeddings.embed_query(src['text']) for src in sources])
    sims = cosine_similarity(answer_emb, chunk_embs)[0]
    return float(np.max(sims))

def highlight_sources(answer: str, sources: List[Dict]) -> List[Dict]:
    # Simple highlight: mark the chunk with highest similarity
    answer_emb = np.array(embeddings.embed_query(answer)).reshape(1, -1)
    chunk_embs = np.array([embeddings.embed_query(src['text']) for src in sources])
    sims = cosine_similarity(answer_emb, chunk_embs)[0]
    max_idx = int(np.argmax(sims)) if len(sims) > 0 else -1
    for i, src in enumerate(sources):
        src['highlight'] = (i == max_idx)
        src['similarity'] = float(sims[i])
    return sources 
from typing import List, Dict

def rerank_chunks(chunks: List[Dict], query: str) -> List[Dict]:
    # If chunks have 'similarity', sort by it. Otherwise, return as is.
    if chunks and 'similarity' in chunks[0]:
        return sorted(chunks, key=lambda x: x['similarity'], reverse=True)
    return chunks

# TODO: Integrate Cohere/BGE reranker or other model-based reranking here. 
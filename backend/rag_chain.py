import time
from typing import List, Dict, Any
from backend.vector_store import vector_store_manager
from backend.memory import memory_manager
from backend.gemini_wrapper import get_gemini_llm
from backend.grounding_utils import calculate_grounding_score, highlight_sources
from backend.reranker import rerank_chunks

class RAGChain:
    def __init__(self):
        self.llm = get_gemini_llm()
        self.vector_store = vector_store_manager
        self.memory = memory_manager

    def preprocess(self, docs: List[Dict]) -> List[Dict]:
        # TODO: LLM-based cleaning, deduplication, clustering/merging
        return docs

    def semantic_chunk(self, docs: List[Dict]) -> List[Dict]:
        # TODO: Embedding-based chunking, overlap, HyQI
        return docs

    def hyde(self, query: str) -> str:
        # TODO: Generate hypothetical answer for retrieval
        return query

    def self_query(self, query: str) -> str:
        # TODO: Rewrite query for better retrieval
        return query

    def crag_label(self, chunks: List[Dict], answer: str) -> List[Dict]:
        # TODO: Label chunks as Correct/Incorrect/Ambiguous
        for c in chunks:
            c['crag'] = 'Correct'  # stub
        return chunks

    def chain_of_thought(self, query: str, context: str) -> str:
        # Always provide context, even if empty
        return f"Think step by step. {query}\nContext: {context if context else '[No context found in your data store.]'}"

    def self_rag(self, query: str, context: str, confidence: float) -> str:
        # TODO: Rerun with enhanced context if confidence is low
        return None

    def run_chat(self, query: str, session_id: str) -> Dict[str, Any]:
        start = time.time()
        memory = self.memory.get_memory(session_id)
        try:
            # Self-query
            retrieval_query = self.self_query(query)
            # HyDE
            hyde_query = self.hyde(retrieval_query)
            # Retrieve
            try:
                retrieved = self.vector_store.search(hyde_query)
            except Exception as e:
                retrieved = []
            chunks = [
                {"text": doc[0].page_content, "metadata": doc[0].metadata, "similarity": doc[1]} for doc in retrieved if hasattr(doc[0], 'page_content')
            ] if retrieved else []
            # Rerank
            reranked = rerank_chunks(chunks, query) if chunks else []
            # Chain-of-thought prompt
            context = "\n".join([c["text"] for c in reranked]) if reranked else ""
            cot_prompt = self.chain_of_thought(query, context)
            # LLM answer (streamed)
            answer = ""
            if context.strip():
                try:
                    for chunk in self.llm.stream_response(cot_prompt):
                        answer += chunk
                except Exception as e:
                    answer = f"[LLM Error: {e}]"
            else:
                answer = "No relevant data found in your knowledge base. Please upload documents or URLs first."
            # CRAG labeling
            labeled = self.crag_label(reranked, answer) if reranked else []
            # Grounding
            grounding_score = calculate_grounding_score(answer, labeled) if labeled else 0.0
            # Self-RAG if low confidence
            if grounding_score < 0.75 and context.strip():
                enhanced = self.self_rag(query, context, grounding_score)
                if enhanced:
                    answer = enhanced
                    grounding_score = calculate_grounding_score(answer, labeled)
            # Highlight sources
            sources = highlight_sources(answer, labeled) if labeled else []
            # Update memory
            memory.save_context({"input": query}, {"output": answer})
            history = memory.buffer
            latency = f"{int((time.time()-start)*1000)}ms"
            return {
                "answer": answer,
                "sources": sources,
                "grounding_score": grounding_score,
                "history": history,
                "latency": latency
            }
        except Exception as e:
            return {
                "answer": f"[Internal Error: {e}]",
                "sources": [],
                "grounding_score": 0.0,
                "history": [],
                "latency": f"{int((time.time()-start)*1000)}ms"
            }

rag_chain = RAGChain() 
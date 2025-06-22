import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List, Dict, Any

class VectorStoreManager:
    def __init__(self, index_path: str = "data/faiss_index"):
        self.index_path = index_path
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = None
        self._load_or_create()

    def _load_or_create(self):
        if os.path.exists(self.index_path):
            self.vectorstore = FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
        else:
            # Create a dummy index with a single init vector
            self.vectorstore = FAISS.from_texts(["init"], self.embeddings)
            self.save()

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        # If the index only contains the dummy 'init' vector, recreate from scratch
        if self.vectorstore is not None and hasattr(self.vectorstore, 'index') and self.vectorstore.index.ntotal == 1:
            self.vectorstore = FAISS.from_texts(texts, self.embeddings, metadatas=metadatas)
        else:
            self.vectorstore.add_texts(texts, metadatas)
        self.save()

    def search(self, query: str, k: int = 4):
        return self.vectorstore.similarity_search_with_score(query, k=k)

    def save(self):
        self.vectorstore.save_local(self.index_path)

    def reset(self):
        # Remove the entire index directory to avoid dimension mismatch
        if os.path.exists(self.index_path):
            for f in os.listdir(self.index_path):
                os.remove(os.path.join(self.index_path, f))
        # Recreate dummy index
        self.vectorstore = FAISS.from_texts(["init"], self.embeddings)
        self.save()

vector_store_manager = VectorStoreManager() 
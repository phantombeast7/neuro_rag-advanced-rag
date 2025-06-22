from langchain_community.document_loaders import (
    PDFPlumberLoader, CSVLoader, TextLoader, Docx2txtLoader, UnstructuredMarkdownLoader
)
from langchain.schema import Document
from typing import List
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def load_document(file_path: str) -> List[Document]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PDFPlumberLoader(file_path)
    elif ext == ".csv":
        loader = CSVLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".md":
        loader = UnstructuredMarkdownLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return loader.load()

def load_url(url: str, max_pages: int = 20) -> List[Document]:
    visited = set()
    to_visit = [url]
    docs = []
    domain = urlparse(url).netloc
    session = requests.Session()
    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        try:
            resp = session.get(current_url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            docs.append(Document(page_content=text, metadata={"source": current_url}))
            visited.add(current_url)
            # Find all internal links
            for a in soup.find_all("a", href=True):
                link = urljoin(current_url, a["href"])
                if urlparse(link).netloc == domain and link not in visited and link not in to_visit:
                    to_visit.append(link)
        except Exception:
            visited.add(current_url)
            continue
    return docs 
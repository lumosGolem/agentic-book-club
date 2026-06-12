import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss

BOOKS_DIR = Path(__file__).parent / "books"
MODEL_ID = "all-MiniLM-L6-v2"

class SharedBookKnowledgeBase:
    def __init__(self):
        self.encoder = SentenceTransformer(MODEL_ID, device="cuda")
        self.chunks = []
        self._load_books()
        self._build_index()

    def _load_books(self):
        # Dynamically ingest all markdown files inside book-store/books/
        for md_file in BOOKS_DIR.glob("*.md"):
            with open(md_file, "r", encoding="utf-8") as f:
                self.chunks.extend([p.strip() for p in f.read().split("\n\n") if len(p.strip()) > 50])

    def _build_index(self):
        embeddings = self.encoder.encode(self.chunks, convert_to_numpy=True)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def query(self, text: str) -> str:
        query_vector = self.encoder.encode([text], convert_to_numpy=True)
        _, indices = self.index.search(query_vector, 3)
        return "\n\n---\n\n".join([self.chunks[idx] for idx in indices[0] if idx != -1])

# Singular internal object instance
SHARED_KB = SharedBookKnowledgeBase()

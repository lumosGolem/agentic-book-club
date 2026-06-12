import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss

# Absolute anchor paths relative to this file's location
CURRENT_DIR = Path(__file__).parent
BOOKS_DIR = CURRENT_DIR / "books"
STORAGE_DIR = CURRENT_DIR / "book-case"
MODEL_ID = "all-MiniLM-L6-v2"
class SharedBookKnowledgeBase:
    def __init__(self):
        # Public lightweight model handles encoding onto GPU memory
        self.encoder = SentenceTransformer(MODEL_ID, device="cuda")
        self.chunks = []
        
        self._ingest_all_markdown_books()
        self._initialize_vector_store()

    def _ingest_all_markdown_books(self):
        # Recursively search author directories for markdown assets
        for md_path in BOOKS_DIR.glob("**/*.md"):
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Split book structural text strictly by paragraph breaks
            paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50]
            self.chunks.extend(paragraphs)

    def _initialize_vector_store(self):
        embeddings = self.encoder.encode(self.chunks, convert_to_numpy=True)
        dimension = embeddings.shape[1]
        
        # Build memory index structure
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        # Save structural checkpoint to book-case/ directory
        os.makedirs(STORAGE_DIR, exist_ok=True)
        faiss.write_index(self.index, str(STORAGE_DIR / "index.faiss"))

    def similarity_search(self, query: str, top_k: int = 3) -> str:
        query_vector = self.encoder.encode([query], convert_to_numpy=True)
        _, indices = self.index.search(query_vector, top_k)
        
        matched_text = [self.chunks[idx] for idx in indices[0] if idx != -1]
        return "\n\n---\n\n".join(matched_text)

# Global singleton object available to the entire system execution context
SHARED_KB = SharedBookKnowledgeBase()

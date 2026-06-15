
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
from dotenv import load_dotenv

# Absolute anchor paths relative to this file's location
CURRENT_DIR = Path(__file__).parent
BOOKS_DIR = CURRENT_DIR / "books"
STORAGE_DIR = CURRENT_DIR / "book_case"
load_dotenv(dotenv_path=CURRENT_DIR / ".env") #token
MODEL_ID = "all-MiniLM-L6-v2"

class SharedBookKnowledgeBase:
    def __init__(self):
        # CHANGE to cuda if GPU and change fais-cuda
        self.encoder = SentenceTransformer(MODEL_ID, device="cpu")
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
        
        if not self.chunks:
            print(f"Warning: No valid markdown text found in {BOOKS_DIR}. Initializing empty index.")
            dimension = 384 # Default dimension for all-MiniLM-L6-v2
            self.index = faiss.IndexFlatL2(dimension)
            return

        embeddings = self.encoder.encode(self.chunks, convert_to_numpy=True)
        dimension = embeddings.shape[1]
        
        # Build memory index structure
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        # Save structural checkpoint to book_case/ directory
        os.makedirs(STORAGE_DIR, exist_ok=True)
        faiss.write_index(self.index, str(STORAGE_DIR / "index.faiss"))

    def similarity_search(self, query: str, top_k: int = 3) -> str:
        
        if not self.chunks or self.index.ntotal == 0:
            return "Knowledge base is empty."

        query_vector = self.encoder.encode([query], convert_to_numpy=True)
        _, indices = self.index.search(query_vector, top_k)
        
        matched_text = [self.chunks[idx] for idx in indices[0] if idx != -1 and idx < len(self.chunks)]
        return "\n\n---\n\n".join(matched_text)

# Global object
SHARED_KB = SharedBookKnowledgeBase()
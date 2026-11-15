from typing import Dict, List, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.features.query.embeddings import build_tfidf_index, query_index


class VectorStore:
    """
    In-memory TF-IDF index store keyed by document_id.
    Why in-memory: for a demo/viva project, this avoids the complexity of
    a vector database. The index is rebuilt on first query after a server
    restart (from the chunk texts stored in SQLite).
    For production, replace with ChromaDB or FAISS with persistent storage.
    """

    def __init__(self):
        # Maps document_id -> (vectorizer, matrix, chunk_texts)
        self._store: Dict[int, Tuple[TfidfVectorizer, np.ndarray, List[str]]] = {}

    def build_for_document(self, document_id: int, chunk_texts: List[str]) -> None:
        """Build and cache the TF-IDF index for a document's chunks."""
        if not chunk_texts:
            return
        vectorizer, matrix = build_tfidf_index(chunk_texts)
        self._store[document_id] = (vectorizer, matrix, chunk_texts)

    def query(
        self, document_id: int, question: str, top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Return top-k (chunk_text, score) pairs for a question.
        Returns empty list if no index exists for this document.
        """
        if document_id not in self._store:
            return []
        vectorizer, matrix, chunk_texts = self._store[document_id]
        return query_index(vectorizer, matrix, chunk_texts, question, top_k)

    def invalidate(self, document_id: int) -> None:
        """Remove a document's index (e.g. when the document is deleted)."""
        self._store.pop(document_id, None)


# Module-level singleton shared across requests within a process.
vector_store = VectorStore()

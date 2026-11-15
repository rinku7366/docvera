from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_tfidf_index(chunks: List[str]) -> Tuple[TfidfVectorizer, np.ndarray]:
    """
    Build a TF-IDF index over a list of text chunks.

    IMPORTANT — what this actually is:
    This uses classical TF-IDF (Term Frequency-Inverse Document Frequency)
    from scikit-learn. It is NOT a neural embedding model. It represents
    text as a sparse vector of word importance scores. It works well for
    keyword-rich queries but does not understand synonyms or semantics.
    For a production system, consider replacing with sentence-transformers
    (e.g. all-MiniLM-L6-v2) for semantic search.

    Returns: (vectorizer, matrix) where matrix has shape (n_chunks, n_terms).
    """
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(chunks)
    return vectorizer, matrix


def query_index(
    vectorizer: TfidfVectorizer,
    matrix: np.ndarray,
    chunk_texts: List[str],
    question: str,
    top_k: int = 5,
) -> List[Tuple[str, float]]:
    """
    Retrieve the top-k most relevant chunks for a question using cosine similarity.
    Returns list of (chunk_text, score) sorted by descending score.
    """
    question_vec = vectorizer.transform([question])
    scores = cosine_similarity(question_vec, matrix).flatten()
    top_indices = scores.argsort()[::-1][:top_k]
    return [(chunk_texts[i], float(scores[i])) for i in top_indices if scores[i] > 0]

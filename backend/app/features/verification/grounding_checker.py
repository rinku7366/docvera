from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Threshold chosen for the demo: claims scoring >= 0.15 cosine similarity
# with a source chunk are considered grounded. Adjust for production.
GROUNDING_THRESHOLD = 0.15


def check_claim_grounding(claim: str, source_chunks: List[str]) -> Dict[str, Any]:
    """
    Measure how well a claim is supported by the source chunks using TF-IDF cosine similarity.

    What this actually does:
    - Vectorises the claim and all source chunks using TF-IDF.
    - Computes cosine similarity between the claim vector and each chunk vector.
    - A claim is "grounded" if its best similarity score >= GROUNDING_THRESHOLD.

    This is NOT a neural entailment model. It detects keyword overlap, not
    logical entailment. It will miss paraphrased claims that use different words.
    Good enough for demonstration; for production use NLI models (e.g. cross-encoder).
    """
    if not source_chunks:
        return {
            "claim": claim,
            "is_grounded": False,
            "best_chunk": "",
            "score": 0.0,
        }

    all_texts = [claim] + source_chunks
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(all_texts)
        claim_vec = matrix[0]
        chunk_matrix = matrix[1:]
        scores = cosine_similarity(claim_vec, chunk_matrix).flatten()
    except ValueError:
        # TfidfVectorizer raises ValueError if vocabulary is empty
        return {"claim": claim, "is_grounded": False, "best_chunk": "", "score": 0.0}

    best_idx = int(scores.argmax())
    best_score = float(scores[best_idx])

    return {
        "claim": claim,
        "is_grounded": best_score >= GROUNDING_THRESHOLD,
        "best_chunk": source_chunks[best_idx][:300],
        "score": round(best_score, 4),
    }

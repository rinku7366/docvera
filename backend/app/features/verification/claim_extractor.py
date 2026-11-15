import re
from typing import List


def extract_claims(answer_text: str) -> List[str]:
    """
    Split an answer into individual claim sentences.

    What this actually does:
    Simple sentence-level splitting using punctuation heuristics.
    This is NOT an NLP model (no spaCy, no transformer). It splits on
    '. ', '! ', '? ' boundaries. Sufficient for demonstrating the
    verification concept in a viva.

    For production, use a proper sentence tokenizer (e.g. spaCy or NLTK).
    """
    # Normalize whitespace first
    text = answer_text.strip()
    # Split on sentence-ending punctuation followed by whitespace + capital letter
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z\[])', text)
    # Filter out very short fragments (less than 10 chars) — likely not real claims
    claims = [s.strip() for s in sentences if len(s.strip()) >= 10]
    return claims if claims else [text]

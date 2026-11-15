from typing import List, Dict, Any
from app.models.document import ChunkType


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Split a long text string into overlapping chunks.
    Why overlapping: questions often straddle sentence boundaries; overlap ensures
    the retriever can find context that would be split across hard boundaries.
    chunk_size and overlap are in characters (not tokens) for simplicity.
    Returns list of {text, chunk_type: TEXT}.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text_str = text[start:end].strip()
        if chunk_text_str:
            chunks.append({"text": chunk_text_str, "chunk_type": ChunkType.TEXT})
        start += chunk_size - overlap
    return chunks


def chunk_table_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert each CSV row into a single chunk.
    Why: table rows are chunked separately from prose text so that
    structured data (e.g. 'Client: Acme, Amount: $500') can be retrieved
    at row-level granularity. Mixing rows into prose chunks would lose
    the row-boundary semantics.
    Each row dict is flattened to 'key: value, key: value' format.
    Returns list of {text, chunk_type: TABLE}.
    """
    chunks = []
    for row_data in rows:
        row_dict = row_data.get("row_dict", {})
        # Flatten row to a readable string: "Column: value, Column: value"
        text = ", ".join(f"{k}: {v}" for k, v in row_dict.items() if v)
        if text.strip():
            chunks.append({"text": text, "chunk_type": ChunkType.TABLE})
    return chunks

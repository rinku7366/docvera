from typing import List, Tuple, Dict, Any


def generate_answer(
    question: str,
    retrieved_chunks: List[Tuple[str, float]],
    language: str = "en",
    plain_language: bool = False,
) -> Dict[str, Any]:
    """
    Construct an answer from the retrieved document chunks.

    IMPORTANT — what this actually does:
    This function does NOT call an external LLM API (like OpenAI or Gemini).
    It assembles an answer by:
      1. Selecting the top retrieved chunks as evidence.
      2. Returning them as direct quotations with the question echoed.
    This is an extractive approach — the "answer" is the most relevant
    source passage(s), presented clearly. This is honest and verifiable,
    unlike a generative model which can hallucinate.

    For production, replace this with a call to an LLM that is prompted
    with the retrieved context (Retrieval-Augmented Generation).

    plain_language: if True, adds a note to read the excerpts carefully.
    language: target language code (translation applied in service layer).
    """
    if not retrieved_chunks:
        return {
            "answer_text": "No relevant content was found in this document for your question.",
            "citations": [],
        }

    citations = []
    answer_parts = []

    for i, (chunk_text, score) in enumerate(retrieved_chunks):
        citation_num = i + 1
        # Take first 300 chars as the displayed excerpt
        excerpt = chunk_text[:300].strip()
        citations.append({
            "citation_num": citation_num,
            "chunk_index": i,
            "excerpt": excerpt,
            "score": round(score, 4),
        })
        # The answer quotes the excerpt with a superscript marker
        answer_parts.append(f"[{citation_num}] {excerpt}")

    answer_text = "\n\n".join(answer_parts)

    if plain_language:
        preamble = (
            "Here are the most relevant passages from your document. "
            "Read the numbered sections below — they contain the answer to your question.\n\n"
        )
        answer_text = preamble + answer_text

    return {
        "answer_text": answer_text,
        "citations": citations,
    }

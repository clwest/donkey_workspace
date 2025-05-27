"""Token helper utilities with optional ``tiktoken`` support."""

try:
    import tiktoken
except Exception:  # pragma: no cover - optional dependency may be absent
    tiktoken = None

EMBEDDING_MODEL = "text-embedding-3-small"
MAX_TOKENS = 8000
if tiktoken:
    encoding = tiktoken.encoding_for_model(EMBEDDING_MODEL)
else:  # simple whitespace-based fallback
    encoding = None


def count_tokens(text: str) -> int:
    """Return the number of tokens in ``text`` using ``tiktoken`` if available."""
    if encoding:
        return len(encoding.encode(text))
    # crude fallback when tiktoken isn't installed
    return len(text.split())


def smart_chunk_prompt(text: str, max_tokens: int = MAX_TOKENS) -> list[dict]:
    """Split ``text`` into token-limited chunks.

    The text is divided on blank lines and grouped so each chunk stays under
    ``max_tokens`` tokens.  Returns a list of dictionaries containing the chunk
    text under ``section`` and its token count under ``tokens``.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_token_count = 0

    for para in paragraphs:
        tokens = count_tokens(para)
        if current_token_count + tokens > max_tokens:
            if current_chunk:
                combined = "\n\n".join(current_chunk)
                chunks.append(
                    {
                        "section": combined,
                        "tokens": count_tokens(combined),
                    }
                )
            current_chunk = [para]
            current_token_count = tokens
        else:
            current_chunk.append(para)
            current_token_count += tokens

    if current_chunk:
        combined = "\n\n".join(current_chunk)
        chunks.append(
            {
                "section": combined,
                "tokens": count_tokens(combined),
            }
        )

    return chunks


__all__ = [
    "EMBEDDING_MODEL",
    "MAX_TOKENS",
    "count_tokens",
    "smart_chunk_prompt",
]

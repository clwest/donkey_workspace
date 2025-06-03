import re


class AcronymGlossaryService:
    """Utility to detect acronyms and inject glossary notes."""

    KNOWN = {
        "MCP": "Model Context Protocol",
        "LLM": "Large Language Model",
        "SDK": "Software Development Kit",
    }

    @classmethod
    def extract(cls, text: str) -> dict:
        """Return mapping of found acronyms to expansions."""
        terms = set(re.findall(r"\b[A-Za-z]{2,}\b", text or ""))
        results = {}
        lowered = text.lower() if text else ""
        for term in terms:
            lookup = term.upper()
            expansion = cls.KNOWN.get(lookup)
            if expansion and expansion.lower() not in lowered:
                results[lookup] = expansion
        return results

    @classmethod
    def prepend_glossary(cls, chunks: list[str]) -> list[str]:
        """Insert glossary definition chunks at the start of ``chunks``."""
        if not chunks:
            return chunks
        full_text = " ".join(chunks)
        mapping = cls.extract(full_text)
        if not mapping:
            return chunks
        intros = [f"{a} refers to {b}." for a, b in mapping.items()]
        for intro in reversed(intros):
            if not chunks[0].startswith(intro):
                chunks.insert(0, intro)
        return chunks

    # Backwards compatible alias
    insert_glossary_chunk = prepend_glossary

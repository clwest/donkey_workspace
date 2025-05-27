import json
import re
from typing import Dict, Any, List


def _parse_key_value_block(block: str) -> Dict[str, Any]:
    """Parse simple ``key: value`` lines into a dictionary."""
    data: Dict[str, Any] = {}
    for line in block.splitlines():
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip().lower()
        value = value.strip()
        # handle comma-separated lists
        if ',' in value:
            items: List[str] = [v.strip() for v in value.split(',') if v.strip()]
            data[key] = items
            continue
        # booleans
        if value.lower() in {'true', 'false'}:
            data[key] = value.lower() == 'true'
            continue
        # numbers
        try:
            data[key] = float(value) if '.' in value else int(value)
            continue
        except ValueError:
            pass
        data[key] = value
    return data


def parse_rag_metadata(text: str) -> Dict[str, Any]:
    """Extract RAG metadata from a prompt response.

    The response may contain a JSON block or ``key: value`` lines
    enclosed in ``[RAG]`` ... ``[/RAG]`` markers or preceded by a
    ``RAG:`` prefix.  Unknown formats return an empty dict.
    """
    if not text:
        return {}

    block = None

    # [RAG]{...json...}[/RAG]
    match = re.search(r"\[RAG\](.*?)\[/RAG\]", text, re.DOTALL | re.IGNORECASE)
    if match:
        block = match.group(1).strip()
    else:
        # RAG: {json}
        match = re.search(r"RAG(?: Metadata)?:\s*(\{.*?\})", text, re.DOTALL | re.IGNORECASE)
        if match:
            block = match.group(1).strip()
        else:
            # RAG metadata lines at end
            match = re.search(r"RAG(?: Metadata)?:\s*(.*)$", text, re.IGNORECASE | re.MULTILINE)
            if match:
                block = match.group(1).strip()

    if not block:
        return {}

    # Try JSON first
    try:
        return json.loads(block)
    except json.JSONDecodeError:
        return _parse_key_value_block(block)

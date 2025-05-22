from __future__ import annotations

def analyze_thought_integrity(content: str) -> str:
    if not content or len(content.strip()) < 10:
        return "empty"
    if "```json" in content and "{" not in content:
        return "markdown_stub"
    lower = content.lower()
    if "error" in lower or "traceback" in content:
        return "error_log"
    return "valid"

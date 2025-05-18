from prompts.utils.token_helpers import count_tokens, MAX_TOKENS


def auto_reduce_prompt(text: str, max_tokens: int = MAX_TOKENS) -> str:
    """
    Automatically reduce a prompt by excluding the least important sections
    (based on token size or order), until it fits within the token limit.
    """
    paragraphs = text.split("\n\n")
    tokenized = [(para, count_tokens(para)) for para in paragraphs]
    total = sum(t for _, t in tokenized)

    if total <= max_tokens:
        return text

    # Trim paragraphs from the end until we fit
    included = []
    current_tokens = 0
    for para, tokens in tokenized:
        if current_tokens + tokens > max_tokens:
            break
        included.append(para)
        current_tokens += tokens

    return "\n\n".join(included)

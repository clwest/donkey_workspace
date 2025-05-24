from embeddings.helpers.helpers_processing import generate_embedding

class CodexRetryStrategy:
    """Simple retry logic to regenerate embeddings with heuristics."""

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def retry_embedding(self, text: str):
        if not text:
            return None
        attempt = 0
        current = text
        while attempt < self.max_attempts:
            vector = generate_embedding(current)
            if vector is not None:
                return vector
            # naive collapse: shorten text for retry
            current = current[: max(100, len(current) // 2)]
            attempt += 1
        return None

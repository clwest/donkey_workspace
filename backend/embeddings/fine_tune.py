import logging

logger = logging.getLogger("django")

# ✅ Minimum similarity threshold (filter out weak matches)
MIN_SIMILARITY_THRESHOLD = 0.2  # Adjust as needed

# ✅ Maximum number of results to return
MAX_RESULTS = 10  # Adjust as needed


def filter_similar_results(results):
    """
    Filters similar results based on a threshold and returns the top matches.

    Args:
        results (list): List of (UUID, similarity_score) tuples.

    Returns:
        list: Filtered and sorted results.
    """
    if not results:
        return []

    # ✅ Filter out weak matches
    filtered_results = [
        (id, sim) for id, sim in results if sim >= MIN_SIMILARITY_THRESHOLD
    ]

    # ✅ Sort by similarity (descending) and limit the results
    sorted_results = sorted(filtered_results, key=lambda x: x[1], reverse=True)[
        :MAX_RESULTS
    ]

    logger.info(f"📊 Fine-tuned results (Top {MAX_RESULTS}): {sorted_results}")

    return sorted_results

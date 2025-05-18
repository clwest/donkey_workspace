import re
from assistants.models import Topic
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
import spacy
import numpy as np
from spacy.matcher import Matcher

# Initialize spaCy
nlp = spacy.load("en_core_web_sm")

logger = logging.getLogger("django")


def get_topics(tfidf_matrix, feature_names, n_top_words=10, model_type="NMF"):
    """
    Using LDA or NMF to identify the topics of interest.
    """
    if (
        tfidf_matrix is None
        or not hasattr(tfidf_matrix, "shape")
        or tfidf_matrix.shape[0] == 0
    ):
        logger.warning("⚠️ TF-IDF matrix is empty or invalid. Skipping topic modeling.")
        return []

    try:
        model = (
            NMF(n_components=5, random_state=1)
            if model_type == "NMF"
            else LatentDirichletAllocation(n_components=5, random_state=1)
        )
        model.fit(tfidf_matrix)

        topics = []
        for topic_idx, topic in enumerate(model.components_):
            top_words = [
                feature_names[i]
                for i in topic.argsort()[
                    : -n_top_words - 1 : -1
                ]  # ✅ Fix: Reverse order to get top words
            ]
            topics.append(top_words)

        logger.info(f"✅ Generated topics: {topics}")
        return topics

    except Exception as e:
        logger.error(f"🚨 Error in topic modeling: {str(e)}")
        return []


def detect_topic(user_message):
    """
    Detects the topic of a user message based on predefined keywords.

    Args:
        user_message (str): The user's input message.

    Returns:
        str: The detected topic or 'General' if no match is found.
    """
    user_message = user_message.lower()
    topics = Topic.objects.all()

    best_match = None
    max_score = 0

    for topic in topics:
        keywords = topic.keywords.split(",")
        relevance_score = sum(
            1 for keyword in keywords if keyword.strip().lower() in user_message
        )

        if relevance_score > max_score:
            best_match = topic.name
            max_score = relevance_score

    return best_match or "General"  # Always return a valid topics

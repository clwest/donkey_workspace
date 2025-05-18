import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
from sklearn.feature_extraction.text import TfidfVectorizer
from keybert import KeyBERT
from textblob import TextBlob
from sklearn.decomposition import NMF, LatentDirichletAllocation
import logging
import spacy
from spacy.matcher import Matcher

from intel_core.core.filters import ALL_STOP_WORDS

# Initialize spaCy
nlp = spacy.load("en_core_web_sm")

logger = logging.getLogger("django")

kw_model = KeyBERT()


def tfidf_transform(corpus):
    """
    Transform a corpus of documents into a TF-IDF matrix.

    Args:
        corpus: List of text documents

    Returns:
        tfidf_matrix: TF-IDF transformed matrix
        feature_names: List of feature names (words)
    """
    if not corpus or len(corpus) == 0:
        logger.warning("Empty corpus provided for TF-IDF transformation")
        return None, []

    try:
        vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english", max_df=0.85, min_df=2
        )
        tfidf_matrix = vectorizer.fit_transform(corpus)
        feature_names = vectorizer.get_feature_names_out()
        return tfidf_matrix, feature_names
    except Exception as e:
        logger.error(f"Error in TF-IDF transformation: {e}")
        return None, []


def lemmatize_text(text, nlp=None):
    """
    Convert words to their base or root form to reduce dimensionality.

    Args:
        text: Text to lemmatize
        nlp: Optional spaCy NLP model (will use default if None)

    Returns:
        str: Lemmatized text
    """
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")

    try:
        doc = nlp(text)
        lemmatized = " ".join([token.lemma_ for token in doc])
        return lemmatized
    except Exception as e:
        logger.error(f"Error lemmatizing text: {e}")
        return text


def extract_entities(text, nlp=None):
    """
    Extract named entities from text using spaCy.

    Args:
        text: Text to extract entities from
        nlp: Optional spaCy NLP model (will use default if None)

    Returns:
        list: List of (entity_text, entity_label) tuples
    """
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")

    try:
        doc = nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        return []


def get_topics(tfidf_matrix, feature_names, n_top_words=10, model_type="NMF"):
    """
    Using LDA or NMF to identify the topics of interest.

    Args:
        tfidf_matrix: TF-IDF transformed matrix
        feature_names: List of feature names (words)
        n_top_words: Number of top words to include per topic
        model_type: Type of model to use ("NMF" or "LDA")

    Returns:
        list: List of topics, where each topic is a list of words
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
            top_features_ind = topic.argsort()[: -n_top_words - 1 : -1]
            top_features = [feature_names[i] for i in top_features_ind]
            topics.append(top_features)

        return topics
    except Exception as e:
        logger.error(f"Error in topic modeling: {e}")
        return []


def spacy_ner(text):
    """Extract named entities from text using Spacy."""
    if not text or len(text.strip()) < 10:
        return []

    doc = nlp(text)

    entities = []
    for ent in doc.ents:
        # Filter out useless junk (very short words, generic words)
        if len(ent.text) > 2 and ent.label_ not in [
            "CARDINAL",
            "ORDINAL",
            "QUANTITY",
            "PERCENT",
            "MONEY",
        ]:
            entities.append(ent.text)
    return list(set(entities))  # Remove duplicates


def keybert_extract(text, top_n=5):
    """Extract key phrases using KeyBERT with improved filtering."""
    if not text or len(text.strip()) < 10:  # Avoid short or empty inputs
        return []

    keywords = kw_model.extract_keywords(
        text, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=top_n
    )

    filtered_keywords = [
        kw[0]
        for kw in keywords
        if kw[0].lower() not in ALL_STOP_WORDS  # Remove common stopwords
        and len(kw[0].split()) > 1  # Keep only multi-word phrases
    ]

    return filtered_keywords


def text_to_tokens(text, nlp):
    """
    Convert text into a list of tokens using spaCy.
    """
    doc = nlp(text)
    return [token.text for token in doc]


def get_sentiment(text):
    """
    Sentiment analysis of text.
    """
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

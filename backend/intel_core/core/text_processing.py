import re
import logging
import spacy
from spacy.matcher import Matcher

# Initialize spaCy
nlp = spacy.load("en_core_web_sm")

logger = logging.getLogger("django")


def clean_text(text):
    """
    Remove special characters, extra whitespaces, and convert text to lowercase.
    """
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[^\w\s]", "", text)  # Remove special characters
    text = re.sub(r"\b\w*\d\w*\b", "", text)  # Remove words containing numbers
    text = re.sub(r"\s+", " ", text)  # Replace multiple spaces with a single space
    return text.strip().lower()  # Ensure no trailing spaces and convert to lowercase


def lemmatize_text(text, nlp):
    """
    Convert words to their base or root form to reduce dimensionality.
    """
    doc = nlp(text)
    lemmatized = " ".join([token.lemma_ for token in doc])
    return lemmatized

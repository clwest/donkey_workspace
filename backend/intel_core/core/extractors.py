import os
import re
import logging
from collections import Counter

# NLP & ML Libraries
import spacy
import nltk
import numpy as np
from nltk.corpus import words
from keybert import KeyBERT
from bs4 import BeautifulSoup as Soup
from sklearn.feature_extraction.text import TfidfVectorizer
from spacy.matcher import Matcher
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Project Modules
from .transformers import keybert_extract, text_to_tokens, spacy_ner
from .topic_modeling import get_topics
from .text_processing import clean_text, lemmatize_text
from .constants import (
    ALLOWED_NAMES,
    IGNORE_LIST,
    COMMON_VAGUE_WORDS,
    ENGLISH_WORDS,
    NAME_PATTERNS,
    CUSTOM_IGNORE_WORDS,
    COMMON_COMPANIES,
)
from intel_core.helpers.nltk_data_loader import ensure_nltk_data

# Environment Variables
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Logger Setup
logger = logging.getLogger("django")

# Instead of directly downloading, use the centralized function
ensure_nltk_data("words")

# NLP Model Initialization
nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()
summarizer = LsaSummarizer()

# ────────────────────────────────────────────────────────────
# 🔹 TITLE & METADATA EXTRACTION
# ────────────────────────────────────────────────────────────


def extract_title(html_content, keyword_tags=["h1", "h2", "h3", "meta"]):
    """Extracts keywords from an HTML document based on provided tags."""
    try:
        soup = Soup(html_content, "html.parser")
        return [tag.get_text(strip=True) for tag in soup.find_all(keyword_tags)]
    except Exception as e:
        logger.error(f"❌ Error extracting title: {e}")
        return []


def extract_keywords(html_content, keyword_tags=["h1", "h2", "h3"]):
    """Extracts keywords from an HTML document based on provided tags."""
    soup = Soup(html_content, "html.parser")
    return [tag.string for tag in soup.find_all(keyword_tags)]


def extract_summary_from_text(text, sentence_count=5):
    """Summarizes a given text using Sumy LSA summarizer."""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summary = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary)


def generate_metadata(document):
    """Generates metadata, including a summary, keywords, and named entities."""
    summary = extract_summary_from_text(document, sentence_count=5)
    doc = nlp(document)
    keywords = [chunk.text for chunk in doc.noun_chunks]
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    return {"summary": summary, "keywords": keywords, "entities": entities}


# ────────────────────────────────────────────────────────────
# 🔹 USER NAME EXTRACTION
# ────────────────────────────────────────────────────────────


def extract_name(user_message, recent_topics=None):
    """
    Extracts a user's name using regex & Named Entity Recognition (NER).

    Args:
        user_message (str): The message to extract a name from
        recent_topics (list, optional): Recent topics to filter out false positives

    Returns:
        dict: Dictionary with "user_name" key or empty dict if no name found
    """
    # Ensure the input is valid
    if not user_message or not isinstance(user_message, str):
        logger.warning(f"⚠️ Invalid input to extract_name: {type(user_message)}")
        return {}

    try:
        user_message = user_message.strip()

        # Step 1: Regex-based name extraction
        for pattern in NAME_PATTERNS:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip().lower()

                if validate_name(extracted_name):
                    return {"user_name": extracted_name.capitalize()}

        # Step 2: Named Entity Recognition (NER)
        doc = nlp(user_message)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                extracted_name = ent.text.strip().lower()

                if validate_name(extracted_name):
                    return {"user_name": extracted_name.capitalize()}

        return {}  # No valid name found, return empty dict
    except Exception as e:
        logger.error(f"❌ Error in extract_name: {str(e)}")
        return {}  # Return empty dict on any error


def validate_name(extracted_name, recent_topics=None):
    """Ensures extracted name is valid and not a common word or vague phrase."""
    if extracted_name in ALLOWED_NAMES:
        return True

    # Exclude common company names from being detected as user names
    if extracted_name.lower() in COMMON_COMPANIES:
        logger.info(f"🏢 Ignoring company name '{extracted_name}' from name detection")
        return False

    if extracted_name in IGNORE_LIST or extracted_name in ENGLISH_WORDS:
        logger.warning(
            f"🚨 BLOCKED: '{extracted_name}' is in IGNORE_LIST or ENGLISH_WORDS!"
        )
        return False

    # ✅ Ensure recent_topics is a list before checking
    if not recent_topics:
        recent_topics = []

    if extracted_name in recent_topics:
        logger.warning(f"⚠️ Ignoring '{extracted_name}' as it's part of recent topics.")
        return False

    if extracted_name in COMMON_VAGUE_WORDS:
        logger.warning(
            f"⚠️ Ignoring '{extracted_name}' as it seems like a vague/common topic."
        )
        return False

    if len(extracted_name.split()) > 2:  # Avoid full sentences
        logger.warning(f"⚠️ Suspicious name '{extracted_name}', ignoring.")
        return False

    return True


# ────────────────────────────────────────────────────────────
# 🔹 TOPIC & ENTITY EXTRACTION
# ────────────────────────────────────────────────────────────


def is_specific_topic(topic):
    """
    Determines if a topic is specific enough to be useful.
    Filters out generic terms, stopwords, and articles.

    Args:
        topic (str): The topic to evaluate

    Returns:
        bool: True if the topic is specific, False otherwise
    """
    # Convert to lowercase and strip
    topic = topic.lower().strip()

    # Skip topics that are too short
    if len(topic) < 3:
        return False

    # Skip topics that are just numbers
    if topic.isdigit():
        return False

    # Skip extremely common generic terms and articles
    generic_terms = [
        "the",
        "a",
        "an",
        "this",
        "that",
        "these",
        "those",
        "its",
        "it's",
        "there",
        "their",
        "they",
        "them",
        "some",
        "any",
        "all",
        "no",
        "not",
        "yes",
        "yeah",
        "something",
        "anything",
        "nothing",
        "everything",
        "thing",
        "things",
        "stuff",
        "item",
        "items",
        "way",
        "ways",
        "part",
        "parts",
        "piece",
        "pieces",
        "time",
        "times",
        "day",
        "days",
        "issue",
        "issues",
        "problem",
        "problems",
        "question",
        "questions",
        "information",
        "info",
        "detail",
        "details",
        "example",
        "examples",
        "instance",
        "instances",
        "bit",
        "bits",
        "case",
        "cases",
        "matter",
        "matters",
        "system",
        "systems",
        "program",
        "programs",
        "use",
        "uses",
        "using",
        "user",
        "users",
        "code",
        "codes",
        "coding",
        "file",
        "files",
        "function",
        "functions",
        "method",
        "methods",
        "type",
        "types",
        "class",
        "classes",
        "data",
        "database",
        "databases",
        "setup",
        "config",
        "configuration",
        "ui",
        "ux",
        "friend",
        "person",
        "more",
        "different",
        "specific",
        "new",
        "same",
        "other",
        "message",
        "offer",
        "discussion",
        "response",
        "result",
        "results",
        "adjustment",
        "container",
        "placement",
        "setup",
    ]

    # Skip topics that are just generic terms
    if topic in generic_terms:
        return False

    # Skip topics that start with articles or possessives followed by generic terms
    prefixed_generics = [f"the {term}" for term in generic_terms]
    prefixed_generics.extend([f"my {term}" for term in generic_terms])
    prefixed_generics.extend([f"your {term}" for term in generic_terms])
    prefixed_generics.extend([f"our {term}" for term in generic_terms])
    prefixed_generics.extend([f"their {term}" for term in generic_terms])
    prefixed_generics.extend([f"a {term}" for term in generic_terms])
    prefixed_generics.extend([f"an {term}" for term in generic_terms])

    # Add common phrases to filter out
    common_phrases = [
        "a little",
        "a few",
        "some more",
        "any more",
        "the problem with",
        "the issue with",
        "the thing about",
        "the situation",
        "the context",
        "the background",
        "the details",
        "the information",
        "the process",
        "the question about",
        "the part about",
        "the section",
        "any specific",
        "some specific",
        "what specific",
        "this specific",
        "that specific",
    ]

    prefixed_generics.extend(common_phrases)

    if topic in prefixed_generics:
        return False

    # Check if topic is just a generic two-word combination
    if " " in topic:
        parts = topic.split()
        if len(parts) == 2:
            if (
                parts[0] in ["the", "a", "an", "my", "your", "our", "their"]
                and parts[1] in generic_terms
            ):
                return False

    return True


TOPIC_MAPPINGS = {
    "openais models": "openai models",
    "specific examplesnnresearchers": "specific examples",
    "sarcastic and non-sarcastic statements": "sarcasm detection",
    "your specific preferences": "user preferences",
    "models understanding": "model comprehension",
}

MAX_RECENT_TOPICS = 15

GENERIC_STOPWORDS = {
    "role",
    "discussion",
    "chat",
    "miscellaneous",
    "assistance",
    "issue",
    "some",
    "specific issue",
    "any assistance",
    "the implementation",
    "a great tool",
    "your results",
    "some coding updates",
    "an interesting project",
    "the assistant",
    "the user",
    "this process",
    "this technique",
    "your projects",
    "models topics",
    "a great choice",
    "the suggestions",
    "a few suggestions",
    "a document-term matrix",
    "important words",
    "more specific advice",
    "fine-tuning help",
    "better knowledge",
    "specific data",
    "any specific ideas",
    "various applications",
    "the overall user experience",
    "a way",
    "this topic",
    "your goals",
    "the nuanced nature",
    "assistant model",
}


def clean_and_filter_topics(topics):
    """Cleans extracted topics by removing junk, duplicates, and malformed topics."""

    cleaned_topics = set()

    for topic in topics:
        clean_topic = topic.strip().lower()

        # Remove unwanted special characters (keep spaces and hyphens)
        clean_topic = re.sub(r"[^\w\s-]", "", clean_topic).strip()

        # Fix weird formatting issues (like "nn1" appearing)
        clean_topic = re.sub(r"nn\d+", "", clean_topic).strip()

        # Deduplicate repeated words (e.g., "role role" → "role")
        words = clean_topic.split()
        if len(words) > 1:
            clean_topic = " ".join(sorted(set(words), key=words.index))

        # Merge topic mappings (correct similar topics)
        clean_topic = TOPIC_MAPPINGS.get(clean_topic, clean_topic)

        # Skip generic stopwords
        if clean_topic in GENERIC_STOPWORDS:
            continue

        # Ensure meaningful topic length
        if len(clean_topic) > 3:
            cleaned_topics.add(clean_topic)

    logger.info(f"✅ Refined Topics: {list(cleaned_topics)}")
    return list(cleaned_topics)


def extract_relevant_topics(recent_messages):
    """Extracts key topics using NER, noun chunks, and KeyBERT while filtering out junk."""

    # Step 1: Aggregate recent messages into a single cleaned text string
    message_texts = [
        msg["text"] if isinstance(msg, dict) and "text" in msg else str(msg)
        for msg in recent_messages
    ]
    all_text = " ".join(message_texts).strip().lower()

    if not all_text or len(all_text.split()) < 3:
        logger.warning("⚠️ Not enough valid text found. Using fallback topics.")
        return ["general discussion"]

    # Step 2: Named Entity Recognition (NER) & Noun Chunks Extraction
    try:
        doc = nlp(all_text)
        entities = [
            ent.text.strip()
            for ent in doc.ents
            if ent.label_ in {"ORG", "PRODUCT", "GPE", "PERSON"}
            and ent.text.lower() not in IGNORE_WORDS
        ]
        noun_chunks = [
            chunk.text.strip()
            for chunk in doc.noun_chunks
            if len(chunk.text.split()) > 1 and chunk.text.lower() not in IGNORE_WORDS
        ]
    except Exception as e:
        logger.error(f"⚠️ NER extraction failed: {e}")
        entities, noun_chunks = [], []

    # Step 3: Extract KeyBERT Keywords - Run on Cleaned Noun Chunks Instead of Whole Text
    try:
        keybert_text = (
            " ".join(noun_chunks) if noun_chunks else all_text
        )  # Prioritize structured text
        keybert_keywords = keybert_extract(keybert_text, top_n=5)
    except Exception as e:
        logger.error(f"⚠️ KeyBERT Error: {e}")
        keybert_keywords = []

    # Step 4: Filter and clean topics
    raw_topics = set(entities + noun_chunks + keybert_keywords)
    cleaned_topics = clean_and_filter_topics(raw_topics)

    return cleaned_topics


def extract_hobbies(user_message):
    """Extracts hobbies while filtering out invalid words like 'and', 'or', 'but'."""

    # Extract hobbies using regex (assuming hobbies are comma-separated)
    matches = re.findall(
        r"\b(?:enjoy|like|love|interested in|curious about)\s([\w\s,]+)",
        user_message,
        re.IGNORECASE,
    )

    if not matches:
        return None  # No hobbies found

    extracted_hobbies = [hobby.strip().lower() for hobby in matches[0].split(",")]

    # Filter out invalid words
    refined_hobbies = [
        hobby for hobby in extracted_hobbies if hobby not in INVALID_HOBBY_WORDS
    ]

    return (
        refined_hobbies if refined_hobbies else None
    )  # Return None if no valid hobbies are found


# ────────────────────────────────────────────────────────────
# 🔹 USER DETAIL EXTRACTION (Occupation, Goals, Hobbies)
# ────────────────────────────────────────────────────────────


def extract_user_details(user_message):
    """
    Extracts occupation, goals, and hobbies from user messages using regex.

    Args:
        user_message (str): The message to extract details from

    Returns:
        dict: Dictionary containing extracted user details or empty dict if none found
    """
    if not user_message or not isinstance(user_message, str):
        logger.warning(f"⚠️ Invalid input to extract_user_details: {type(user_message)}")
        return {}

    try:
        extracted_info = {}

        patterns = {
            "occupation": r"(?:i (?:work|am|am employed) (?:as|at|for|with) (.+?))\b",
            "goals": r"(?:my goal is to|i aim to|i want to) (.+?)\b",
            "hobbies": r"(?:i (?:enjoy|love|like|am into|spend time) (.+?))\b",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                extracted_info[key] = match.group(1).strip()

        logger.info(f"🔍 Extracted details from message: {extracted_info}")
        return extracted_info
    except Exception as e:
        logger.error(f"❌ Error in extract_user_details: {str(e)}")
        return {}


# ────────────────────────────────────────────────────────────
# 🔹 MATCHING USER MEMORY WITH EXTRACTED TOPICS
# ────────────────────────────────────────────────────────────


def extract_details_from_message(user_message, extracted_topics, user_memory):
    """Matches extracted topics with user details (hobbies, occupation, goals)."""

    details = {}

    topic_mapping = {
        "hobbies": ["weekend", "relaxation", "plans", "free time"],
        "occupation": ["work", "job", "career", "project"],
        "goals": ["future", "dream", "goal", "aspiration"],
    }

    for key, related_topics in topic_mapping.items():
        if any(topic in extracted_topics for topic in related_topics):
            if user_memory.get(key):
                details[key] = user_memory[key]

    return details  # Example output: {'hobbies': 'paddle boarding'}

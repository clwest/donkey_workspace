from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import re
import logging
from keybert import KeyBERT
from bs4 import BeautifulSoup as Soup
import nltk
import numpy as np
from nltk.corpus import words
from collections import Counter
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from spacy.matcher import Matcher
from .transformers import keybert_extract, text_to_tokens, spacy_ner
from .topic_modeling import get_topics
from .text_processing import clean_text, lemmatize_text
import os
from intel_core.helpers.nltk_data_loader import ensure_nltk_data


logger = logging.getLogger("django")
# Instead of directly downloading, use the centralized function
ensure_nltk_data("words")
# Initialize spaCy
nlp = spacy.load("en_core_web_sm")

SENTIMENT_THRESHOLDS = {
    "positive": 0.2,
    "neutral": (-0.2, 0.2),
    "negative": -0.2,
}

RESPONSE_TEMPLATES = {
    "highly_positive": [
        "That's fantastic to hear! I'm excited to help you build on this positive energy. What's next?"
    ],
    "positive": [
        "That's fantastic to hear! Let me know how I can help you further.",
        "Great! It sounds like you're in a good place. How can I assist you?",
    ],
    "neutral": [
        "Got it. How can I assist you today?",
        "Sure thing. Let me know what you need help with.",
    ],
    "negative": [
        "I'm sorry to hear that. Is there anything I can do to help?",
        "It sounds like you're facing a challenge. I'm here to assist you.",
    ],
}

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_LENGTH = 1536
CHAT_MODEL = "gpt-4o-mini"

# Common adjectives and non-names
COMMON_ADJECTIVES = {
    "good",
    "great",
    "fine",
    "bad",
    "okay",
    "awesome",
    "cool",
    "nice",
    "sure",
    "fantastic",
    "terrible",
}

# Common words that shouldn't be mistaken for names
IGNORE_LIST = {
    "flutter",
    "python",
    "django",
    "ai",
    "bot",
    "assistant",
    "gpt",
    "good",
    "fine",
    "great",
    "okay",
    "cool",
    "happy",
    "sad",
    "excited",
    "strong",
    "smart",
    "fast",
    "lucky",
    "bad",
    "tired",
    "weak",
    "awesome",
}


# List of words/phrases to ignore
IGNORE_WORDS = {
    "role",
    "assistant",
    "user",
    "content",
    "something",
    "everything",
    "that",
    "it",
    "the",
    "you",
    "i",
    "we",
    "they",
    "one",
    "thing",
    "set",
}

# Load a set of real English words (to filter out non-names)
ENGLISH_WORDS = set(words.words())

NAME_PATTERNS = [
    r"\bmy name is ([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b",  # "My name is John Doe"
    r"\byou can call me ([A-Z][a-z]+)\b",  # "You can call me John"
    r"\bi am (?!good|fine|great|okay|cool|happy|sad)([A-Z][a-z]+)\b",  # "I am John" but NOT "I am good"
    r"\bi'm (?!good|fine|great|okay|cool|happy|sad)([A-Z][a-z]+)\b",  # "I'm John" but NOT "I'm good"
    r"\bit's ([A-Z][a-z]+)\b",  # "It's John"
    r"\bthey call me ([A-Z][a-z]+)\b",  # "They call me John"
    r"\bi am ([A-Z][a-z]+( [A-Z][a-z]+)?)\b",
]

# 🚨 Force allow Ted, Alex, and common first names
ALLOWED_NAMES = {"ted", "alex", "john", "mike", "sarah", "lisa", "emma", "james"}

# Common company names to exclude from name detection
COMMON_COMPANIES = {
    "tesla",
    "apple",
    "google",
    "amazon",
    "microsoft",
    "meta",
    "facebook",
    "netflix",
    "nvidia",
    "ibm",
    "intel",
    "amd",
    "twitter",
    "snapchat",
    "uber",
    "lyft",
    "airbnb",
    "slack",
    "zoom",
    "spotify",
    "paypal",
    "square",
    "stripe",
    "shopify",
    "coinbase",
}

CUSTOM_IGNORE_WORDS = {
    "role",
    "assistant",
    "content",
    "user",
    "hey",
    "bot",
    "help",
    "chat",
    "ai",
    "response",
}

COMMON_VAGUE_WORDS = {
    "various",
    "several",
    "some",
    "different",
    "multiple",
    "a number of",
    "a wide range",
    "certain aspects",
    "things",
}

# List of words that should NOT be extracted as hobbies
INVALID_HOBBY_WORDS = {"and", "or", "but", "also", "maybe", "possibly"}


# Generic phrases that lack specificity
COMMON_VAGUE_TOPICS = {
    "this moment",
    "a great opportunity",
    "the event",
    "some time",
    "a moment",
    "the weekend",
    "your own pace",
    "what kinds",
    "any specific types",
    "like-minded individuals",
    "the hackathons",
    "projects bounties",
    "hackathons role",
    "new projects",
    "bounties particularly",
    "what opportunities",
}

# Extracted from chat roles (should be handled separately)
IGNORE_CHAT_METADATA = {"role user", "role assistant", "assistant content", "my end"}

# Too broad and might block useful insights
CONTEXT_DEPENDENT_IGNORE = {
    "time",
    "a monday",
    "the first day",
    "good afternoon",
    "a productive morning",
    "the fundamentals",
    "the hardest thing",
    "course role",
    "that lol",
    "a different idea",
}

# 🔥 Final combined set for use in filtering
IGNORE_TOPICS = COMMON_VAGUE_TOPICS | IGNORE_CHAT_METADATA | CONTEXT_DEPENDENT_IGNORE


# Map vague extracted topics to more meaningful terms

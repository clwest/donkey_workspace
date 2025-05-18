from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

CUSTOM_IGNORE_WORDS = {"trying", "test", "example"}  # Add your own
ALL_STOP_WORDS = ENGLISH_STOP_WORDS.union(CUSTOM_IGNORE_WORDS)

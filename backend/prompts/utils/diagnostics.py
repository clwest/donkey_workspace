# prompts/utils/diagnostics.py

from textstat import textstat
from .token_helpers import count_tokens  # assuming this exists
from prompts.models import Prompt

def update_prompt_diagnostics(prompt: Prompt):
    text = prompt.content or ""
    prompt.token_count = count_tokens(text)
    prompt.flesch_reading_ease = textstat.flesch_reading_ease(text)
    prompt.flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
    prompt.avg_sentence_length = textstat.avg_sentence_length(text)
    prompt.avg_syllables_per_word = textstat.avg_syllables_per_word(text)
    prompt.reading_time_seconds = int(textstat.reading_time(text) * 60)
    prompt.save()
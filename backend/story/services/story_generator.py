# services/story_generator.py
from story.utils.openai_story import generate_story


def run_story_generation(prompt: str, theme: str = None, tags: list = None) -> str:
    return generate_story(prompt, theme, tags)

from typing import Tuple
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_alt_text_and_caption(prompt: str, story_snippet: str) -> Tuple[str, str]:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": (
                    "You're a creative assistant who writes concise image alt-text and fun, engaging captions for children's storybooks. "
                    "Keep alt-text under 1 sentence and the caption whimsical."
                ),
            },
            {
                "role": "user",
                "content": f"Prompt: {prompt}\n\nStory context: {story_snippet}\n\nWrite an alt-text and caption.",
            },
        ],
    )
    content = response.choices[0].message.content.strip()

    # Allow for fallback formatting if needed
    lines = content.split("\n")
    if len(lines) >= 2:
        alt_text = lines[0].replace("Alt-text:", "").strip()
        caption = lines[1].replace("Caption:", "").strip()
    else:
        alt_text, caption = content.strip(), ""

    return alt_text, caption

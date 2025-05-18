from openai import OpenAI
import os
from typing import Tuple, List, Dict, Optional

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_story(
    prompt: str,
    theme: Optional[str] = None,
    tags: Optional[List[str]] = None,
    title: Optional[str] = None,
    project_name: Optional[str] = None,
) -> str:
    system = (
        "You are a whimsical, thoughtful AI who writes delightful, age-appropriate fairy tales. "
        "Your stories always spark imagination, curiosity, and comfort, while avoiding anything scary or inappropriate."
    )

    user_prompt = f"""
        Write a short magical children's story.

        Prompt: "{prompt}"
        Theme: "{theme or 'Surprise me!'}"
        Tags: {', '.join(tags) if tags else 'imaginative, fantasy, friendly'}

        Include:
        - A clear beginning, middle, and end.
        - Positive lessons or themes (e.g., bravery, kindness, curiosity).
        - Wholesome tone and vivid imagination.
        - Avoid violence or anything scary.
    """

    if title:
        user_prompt += f"\nStory Title (if needed): {title}"
    if project_name:
        user_prompt += f"\nPart of a project or series called: {project_name}"

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt.strip()},
        ],
        max_tokens=1000,
        temperature=0.85,
    )

    return response.choices[0].message.content.strip()

# utils/llm.py

import os
from openai import OpenAI
from typing import Literal
from google import genai
from dotenv import load_dotenv
load_dotenv()



# You can swap out or extend with more providers as needed.
DEFAULT_MODEL = "gpt-4o"

client = OpenAI() # or wherever you're loading it

def call_gpt4(prompt: str, model="gpt-4o", max_tokens=512, temperature=0.4) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    # ✅ Ensure we’re returning just the assistant message content
    return response.choices[0].message.content.strip()



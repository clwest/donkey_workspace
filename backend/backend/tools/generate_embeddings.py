import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
load_dotenv()
import django

django.setup()


import tiktoken
from openai import OpenAI
from prompts.models import Prompt
from prompts.utils.embeddings import get_embedding


client = OpenAI()
encoding = tiktoken.encoding_for_model("text-embedding-3-small")
MAX_TOKENS = 8192


def count_tokens(text):
    return len(encoding.encode(text))


def chunk_text(text, max_tokens=8000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        token_count = count_tokens(word)
        if current_length + token_count > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = token_count
        else:
            current_chunk.append(word)
            current_length += token_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def embed_prompts():
    prompts = Prompt.objects.filter(embedding__isnull=True)
    print(f"📦 Found {prompts.count()} prompts needing embeddings...\n")

    for prompt in prompts:
        try:
            token_count = count_tokens(prompt.content)
            if token_count > MAX_TOKENS:
                print(
                    f"⚠️ {prompt.title} exceeds max tokens ({token_count}), chunking..."
                )
                chunks = chunk_text(prompt.content)
                # For now, average all chunk embeddings into one
                chunk_embeddings = [get_embedding(chunk) for chunk in chunks]
                averaged = [
                    sum(values) / len(values) for values in zip(*chunk_embeddings)
                ]
                prompt.embedding = averaged
            else:
                prompt.embedding = get_embedding(prompt.content)

            prompt.save()
            print(f"✅ Embedded: {prompt.title} ({prompt.source})")

        except Exception as e:
            print(f"❌ Failed: {prompt.title} — {e}")


if __name__ == "__main__":
    embed_prompts()

import os
import django
from uuid import uuid4
from dotenv import load_dotenv
from django.utils.text import slugify
import sys


sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
load_dotenv()
django.setup()

from prompts.models import Prompt

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "../prompt_sets")


def ingest_prompts():
    for root, _, files in os.walk(PROMPTS_DIR):
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                with open(full_path, "r") as f:
                    content = f.read()

                title = os.path.splitext(file)[0]
                source = os.path.basename(root).upper()
                prompt = Prompt.objects.create(
                    id=uuid4(),
                    title=title,
                    type="system",
                    content=content,
                    source=source,
                )
                print(f"✅ Ingested {title}")


if __name__ == "__main__":
    ingest_prompts()

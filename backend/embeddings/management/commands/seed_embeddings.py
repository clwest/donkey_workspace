# embeddings/management/commands/seed_embeddings.py
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from embeddings.helpers.helpers_processing import generate_embedding
from embeddings.helpers.helpers_io import save_embedding
from embeddings.models import Embedding
from prompts.models import Prompt
from memory.models import MemoryEntry
from mcp_core.models import Tag

import logging

logger = logging.getLogger("embeddings")


class Command(BaseCommand):
    help = "Generate and save embeddings for all relevant models"

    def handle(self, *args, **kwargs):
        self.stdout.write("🌱 Starting embedding seeding...")

        total_prompt = self.embed_model(Prompt, "content")
        total_memory = self.embed_model(MemoryEntry, "event")

        self.stdout.write(f"🧠 Prompt: Embedded {total_prompt} items.")
        self.stdout.write(f"🧠 MemoryEntry: Embedded {total_memory} items.")
        self.stdout.write("✅ Seeding complete!")

    def embed_model(self, model_class, text_field: str) -> int:
        from embeddings.models import TagConcept
        from embeddings.helpers.helper_tagging import generate_tags_for_memory
        from embeddings.helpers.helpers_processing import generate_embedding
        from embeddings.helpers.helpers_io import (
            save_embedding,
            get_embedding_for_text,
        )  # Ensure this exists or inline

        count = 0
        content_type = ContentType.objects.get_for_model(model_class)

        for obj in model_class.objects.all():
            text = getattr(obj, text_field, "")
            if not text or not text.strip():
                logger.warning(
                    f"⚠️ Skipping {model_class.__name__} {obj.id} — empty or blank {text_field}"
                )
                continue

            existing = Embedding.objects.filter(
                content_type=content_type, content_id=str(obj.id)
            ).exists()

            if existing:
                logger.info(
                    f"↪️ Skipping {model_class.__name__} {obj.id} — embedding already exists"
                )
                continue

            # Generate and attach tags (with valid embeddings)
            if hasattr(obj, "tags") and hasattr(obj.tags, "set") and not obj.tags.exists():
                tags = generate_tags_for_memory(text) or []

                tag_objs = []

                for tag in tags:
                    tag_slug = slugify(tag)

                    # First, try to find by slug or name
                    tag_obj = Tag.objects.filter(slug=tag_slug).first()

                    if not tag_obj:
                        # Prevent slug collision by adding a suffix if needed
                        suffix = 1
                        base_slug = tag_slug
                        while Tag.objects.filter(slug=tag_slug).exists():
                            tag_slug = f"{base_slug}-{suffix}"
                            suffix += 1

                        tag_obj = Tag.objects.create(name=tag, slug=tag_slug)

                    tag_objs.append(tag_obj)

                obj.tags.set(tag_objs)
                obj.save()

            # Generate object embedding
            embedding = generate_embedding(text)
            if embedding:
                save_embedding(obj, embedding)
                count += 1

        return count

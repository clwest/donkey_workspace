# mcp_core/management/commands/seed_memories.py

import random
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from mcp_core.models import MemoryContext, Tag
from project.models import Project
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Seed random important memories for reflection testing."

    def handle(self, *args, **kwargs):
        samples = [
            "Execution speed improved after priority system tuning.",
            "Error rates increased when scaling beyond 100 concurrent tasks.",
            "Latency reduced by implementing task batching.",
            "User satisfaction improved after adding context-aware prompts.",
            "Performance dipped when memory chains exceeded optimal size.",
            "Reflection cycles improved agent decision quality.",
            "Knowledge retrieval system caused bottlenecks under high load.",
            "Expansion modules delayed during peak task volumes.",
            "Unexpected memory overflow detected during nested planning.",
            "Contextual story personalization doubled user retention.",
        ]

        tag_names = ["performance", "user", "scaling", "planning", "memory"]
        tag_objs = {}
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name)
            if not tag.slug:
                tag.slug = slugify(name)
                tag.save()
            tag_objs[name] = tag

        projects = list(Project.objects.all())
        if not projects:
            self.stdout.write(
                self.style.WARNING("⚠️ No projects found! Cannot seed memory contexts.")
            )
            return

        created = 0
        for content in samples:
            project = random.choice(projects)
            context = MemoryContext.objects.create(
                target_object_id=project.id,
                target_content_type=ContentType.objects.get_for_model(Project),
                content=content,
                important=True,
                category="test_seed",
            )

            # Assign tags properly using .set()
            selected_tags = random.sample(list(tag_objs.values()), k=2)
            context.tags.set(selected_tags)

            created += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Seeded {created} memory entries!"))

from django.core.management.base import BaseCommand
from intel_core.models import Document
from assistants.models import Assistant
from prompts.models import Prompt
from prompts.utils.openai_utils import generate_prompt_from_idea
from django.utils.text import slugify
from django.utils import timezone

class Command(BaseCommand):
    help = "Create assistants from document summaries when none linked"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None)

    def handle(self, *args, **options):
        limit = options.get("limit")
        count = 0
        qs = Document.objects.filter(summary__isnull=False)
        if limit:
            qs = qs[:limit]
        for doc in qs:
            if doc.linked_assistants.exists():
                continue
            idea = doc.summary[:800]
            prompt_text = generate_prompt_from_idea(idea)
            if not prompt_text:
                self.stdout.write(self.style.WARNING(f"Failed to generate prompt for {doc.slug}"))
                continue
            prompt = Prompt.objects.create(
                title=f"Auto Prompt {doc.title}"[:255],
                content=prompt_text,
                type="system",
                tone="informative",
                token_count=len(prompt_text.split()),
            )
            assistant = Assistant.objects.create(
                name=doc.title[:80],
                slug=slugify(doc.title)[:50] + "-auto",
                system_prompt=prompt,
                tone="informative",
                specialty="bootstrap",
                is_demo=False,
            )
            assistant.documents.add(doc)
            assistant.created_at = timezone.now()
            assistant.save()
            self.stdout.write(self.style.SUCCESS(f"Created assistant {assistant.slug} for {doc.slug}"))
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Bootstrapped {count} assistants"))

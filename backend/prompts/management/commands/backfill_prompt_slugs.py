from django.core.management.base import BaseCommand
from prompts.models import Prompt
from prompts.utils.token_helpers import count_tokens

class Command(BaseCommand):
    help = "Ensure required prompt slugs exist"

    def add_arguments(self, parser):
        parser.add_argument(
            "--required",
            nargs="+",
            default=[],
            help="List of prompt slugs that must exist",
        )

    def handle(self, *args, **options):
        slugs = options["required"] or []
        created = 0
        for slug in slugs:
            if slug == "reflection-prompt":
                content = (
                    "You are an AI assistant reflecting on memory. "
                    "Extract useful patterns and summarize insights."
                )
            else:
                content = ""
            obj, was_created = Prompt.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": slug.replace("-", " ").title(),
                    "type": "system",
                    "content": content,
                    "source": "fallback",
                    "token_count": count_tokens(content) if content else 0,
                },
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.WARNING(f"Created placeholder prompt '{slug}'"))
        self.stdout.write(self.style.SUCCESS(f"Processed {len(slugs)} slugs (created {created})"))

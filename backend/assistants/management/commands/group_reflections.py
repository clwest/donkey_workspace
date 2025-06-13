from django.core.management.base import BaseCommand
from assistants.models import Assistant
from assistants.models.reflection import ReflectionGroup
from assistants.utils.reflection_summary import summarize_reflections_for_document


class Command(BaseCommand):
    help = "Summarize reflections for a reflection group"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)
        parser.add_argument("--slug", required=True)

    def handle(self, *args, **options):
        assistant_slug = options["assistant"]
        slug = options["slug"]
        assistant = Assistant.objects.get(slug=assistant_slug)
        group, _ = ReflectionGroup.objects.get_or_create(
            assistant=assistant, slug=slug, defaults={"title": slug}
        )
        result = summarize_reflections_for_document(
            group_slug=slug, assistant_id=assistant.id
        )
        if result:
            self.stdout.write(self.style.SUCCESS(f"Updated summary for {slug}"))
        else:
            self.stdout.write(self.style.WARNING("No reflections found"))

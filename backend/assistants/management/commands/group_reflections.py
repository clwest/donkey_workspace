from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from assistants.models.reflection import ReflectionGroup
from assistants.utils.reflection_summary import summarize_reflections_for_document


class Command(BaseCommand):
    help = "Summarize reflections for a reflection group"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)
        parser.add_argument("--slug", required=True)

    def handle(self, *args, **options):
        identifier = options["assistant"]
        slug = options["slug"]
        assistant = resolve_assistant(identifier)
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{identifier}' not found"))
            return
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

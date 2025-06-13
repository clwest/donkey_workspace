from django.core.management.base import BaseCommand
from assistants.models.reflection import ReflectionGroup
from assistants.utils.reflection_summary import summarize_reflections_for_document


class Command(BaseCommand):
    help = "Summarize reflections for a group"

    def add_arguments(self, parser):
        parser.add_argument("--group", required=True, help="Group slug or id")

    def handle(self, *args, **options):
        identifier = options["group"]
        group = (
            ReflectionGroup.objects.filter(id=identifier).first()
            or ReflectionGroup.objects.filter(slug=identifier).first()
        )
        if not group:
            self.stderr.write(self.style.ERROR("Group not found"))
            return
        summarize_reflections_for_document(
            group_slug=group.slug, assistant_id=group.assistant_id
        )
        self.stdout.write(self.style.SUCCESS(f"Summarized {group.slug}"))

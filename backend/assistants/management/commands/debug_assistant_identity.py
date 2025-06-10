from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict
from assistants.models import Assistant


class Command(BaseCommand):
    """Inspect assistant identity settings and simulate /identity/ access."""

    help = "Debug identity access checks for an assistant"

    def add_arguments(self, parser):
        parser.add_argument("--slug", dest="slug", help="Assistant slug", default=None)
        parser.add_argument("--id", dest="id", help="Assistant ID", default=None)
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print all assistant fields",
        )

    def handle(self, *args, **options):
        slug = options.get("slug")
        id_value = options.get("id")
        verbose = options.get("verbose")

        if not slug and not id_value:
            self.stdout.write(self.style.ERROR("Provide --slug or --id"))
            return

        try:
            if slug:
                assistant = Assistant.objects.get(slug=slug)
            else:
                assistant = Assistant.objects.get(id=id_value)
        except Assistant.DoesNotExist:
            self.stdout.write(self.style.ERROR("Assistant not found"))
            return

        self.stdout.write(f"Assistant: {assistant.slug} (ID: {assistant.id})")
        self.stdout.write(f"name: {assistant.name}")
        self.stdout.write(f"is_demo: {assistant.is_demo}")
        if assistant.created_by:
            self.stdout.write(
                f"created_by: {assistant.created_by.username} ({assistant.created_by_id})"
            )
        else:
            self.stdout.write("created_by: None")

        if assistant.is_demo:
            access_msg = self.style.SUCCESS("✅ Allowed (demo assistant)")
        elif assistant.created_by is None:
            access_msg = self.style.ERROR("❌ Forbidden (no owner set)")
        else:
            access_msg = (
                f"❌ Forbidden for others (only {assistant.created_by.username} can access)"
            )

        self.stdout.write(f"Identity Access: {access_msg}")

        if verbose:
            self.stdout.write("\nAll fields:")
            data = model_to_dict(assistant)
            for key, value in data.items():
                self.stdout.write(f"- {key}: {value}")

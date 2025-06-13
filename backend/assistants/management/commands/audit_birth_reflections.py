from django.core.management.base import BaseCommand
from assistants.models import Assistant
import json


class Command(BaseCommand):
    help = "List assistants with birth reflection retries"

    def add_arguments(self, parser):
        parser.add_argument(
            "--failed-only",
            action="store_true",
            help="Show only assistants whose reflection still fails",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output results as JSON",
        )

    def handle(self, *args, **options):
        qs = Assistant.objects.filter(birth_reflection_retry_count__gt=0)
        if options["failed_only"]:
            qs = qs.filter(last_reflection_successful=False)
        data = [
            {
                "slug": a.slug,
                "id": str(a.id),
                "name": a.name,
                "retry_count": a.birth_reflection_retry_count,
                "last_successful": a.last_reflection_successful,
            }
            for a in qs
        ]
        if options["json"]:
            self.stdout.write(json.dumps(data, indent=2))
            return
        if not data:
            self.stdout.write("No retries found")
            return
        for item in data:
            status = "✅" if item["last_successful"] else "❌"
            self.stdout.write(
                f"{item['slug']} ({item['name']}): {item['retry_count']} {status}"
            )

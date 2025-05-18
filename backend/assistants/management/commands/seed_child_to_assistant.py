from django.core.management.base import BaseCommand
from assistants.models import Assistant


class Command(BaseCommand):
    help = "Assigns matching assistants to a parent assistant (e.g., Zeno)"

    def handle(self, *args, **kwargs):
        try:
            parent = Assistant.objects.get(slug="zeno-the-build-wizard")
        except Assistant.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Zeno not found."))
            return

        # Match child assistants by name pattern (customize as needed)
        children = Assistant.objects.filter(name__icontains="LangChain", parent_assistant__isnull=True)

        if not children.exists():
            self.stdout.write(self.style.WARNING("⚠️ No eligible child assistants found."))
            return

        for child in children:
            child.parent_assistant = parent
            child.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Assigned {child.name} to Zeno"))

        self.stdout.write(self.style.SUCCESS("🎉 Child assignment complete."))
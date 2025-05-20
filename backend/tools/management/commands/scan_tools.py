from pathlib import Path
from django.core.management.base import BaseCommand
from django.apps import apps
from tools.utils import discover_tools


class Command(BaseCommand):
    help = "Scan tools/integrations for decorated tool functions"

    def handle(self, *args, **options):
        base_dir = Path(apps.get_app_config("tools").path) / "integrations"
        if not base_dir.exists():
            self.stdout.write(self.style.WARNING(f"No directory: {base_dir}"))
            return
        discover_tools(base_dir)
        self.stdout.write(self.style.SUCCESS("Tool scan complete"))

from django.core.management.base import BaseCommand
from django.core.management import call_command
from assistants.utils.resolve import resolve_assistant
from assistants.models import Assistant
from assistants.utils.trust_profile import update_assistant_trust_cache

class Command(BaseCommand):
    help = "Recalculate and cache trust profile scores"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug or id", required=False)

    def handle(self, *args, **options):
        identifier = options.get("assistant")
        if identifier:
            assistants = [resolve_assistant(identifier)] if resolve_assistant(identifier) else []
            if not assistants:
                self.stderr.write(self.style.ERROR(f"Assistant '{identifier}' not found"))
                return
        else:
            assistants = Assistant.objects.all()
        for a in assistants:
            data = update_assistant_trust_cache(a)
            self.stdout.write(f"{a.slug}: {data['score']} ({data['level']})")


from django.core.management.base import BaseCommand
from django.db import transaction
import json
from ast import literal_eval

class Command(BaseCommand):
    help = "Fix invalid Assistant.capabilities values so migrations can run"

    def handle(self, *args, **options):
        from assistants.models import Assistant

        updated = 0
        with transaction.atomic():
            for assistant in Assistant.objects.all():
                data = assistant.capabilities
                valid = data
                if isinstance(data, str):
                    try:
                        valid = json.loads(data)
                    except json.JSONDecodeError:
                        try:
                            valid = literal_eval(data)
                        except Exception:
                            valid = {}
                if valid is None:
                    valid = {}
                if valid != data:
                    assistant.capabilities = valid
                    assistant.save(update_fields=["capabilities"])
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Updated {updated} assistants"))

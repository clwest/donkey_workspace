from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from assistants.models import Assistant
from assistants.helpers.logging_helper import reflect_on_birth


class Command(BaseCommand):
    help = "Retry a failed birth reflection for an assistant"

    def add_arguments(self, parser):
        parser.add_argument("identifier", help="Assistant slug or UUID")

    def handle(self, *args, **options):
        ident = options["identifier"]
        try:
            assistant = Assistant.objects.get(slug=ident)
        except Assistant.DoesNotExist:
            assistant = get_object_or_404(Assistant, id=ident)

        if assistant.last_reflection_successful:
            self.stdout.write("Reflection already completed")
            return
        if not assistant.can_retry_birth_reflection:
            self.stdout.write("Retry disabled")
            return

        reflect_on_birth(assistant)
        assistant.refresh_from_db()
        assistant.birth_reflection_retry_count += 1
        if assistant.last_reflection_successful:
            assistant.can_retry_birth_reflection = False
        elif assistant.birth_reflection_retry_count >= 3:
            assistant.can_retry_birth_reflection = False
        assistant.save(update_fields=["birth_reflection_retry_count", "can_retry_birth_reflection"])

        if assistant.last_reflection_successful:
            self.stdout.write(self.style.SUCCESS("Reflection retry succeeded"))
        else:
            self.stdout.write(self.style.WARNING("Reflection retry failed"))

from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from assistants.models import Assistant
from assistants.helpers.logging_helper import reflect_on_birth
from devtools.models import DevLog


def retry_for_assistant(assistant: Assistant, command) -> None:
    """Run a retry cycle and update flags."""
    if assistant.last_reflection_successful:
        command.stdout.write("Reflection already completed")
        return
    if not assistant.can_retry_birth_reflection:
        command.stdout.write("Retry disabled")
        return

    reflect_on_birth(assistant)
    assistant.refresh_from_db()
    assistant.birth_reflection_retry_count += 1
    if assistant.last_reflection_successful:
        assistant.can_retry_birth_reflection = False
    elif assistant.birth_reflection_retry_count >= 3:
        assistant.can_retry_birth_reflection = False
    assistant.save(
        update_fields=["birth_reflection_retry_count", "can_retry_birth_reflection"]
    )

    DevLog.objects.create(
        event="birth_reflection_retry",
        assistant=assistant,
        success=assistant.last_reflection_successful,
        details=assistant.reflection_error or "",
    )

    if assistant.last_reflection_successful:
        command.stdout.write(command.style.SUCCESS("Reflection retry succeeded"))
    else:
        command.stdout.write(command.style.WARNING("Reflection retry failed"))


class Command(BaseCommand):
    help = "Retry a failed birth reflection for an assistant"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Retry birth reflection for all eligible assistants",
        )
        parser.add_argument(
            "--assistant",
            dest="assistant",
            help="Assistant slug or UUID to retry",
        )

    def handle(self, *args, **options):
        if options["all"]:
            qs = Assistant.objects.filter(can_retry_birth_reflection=True)
            for a in qs:
                retry_for_assistant(a, self)
            return

        ident = options.get("assistant")
        if not ident:
            self.stderr.write("Provide --assistant or --all")
            return

        try:
            assistant = Assistant.objects.get(slug=ident)
        except Assistant.DoesNotExist:
            assistant = get_object_or_404(Assistant, id=ident)

        retry_for_assistant(assistant, self)

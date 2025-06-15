from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from assistants.utils.trust_profile import TRUST_CACHE_PREFIX, r as redis_client


class Command(BaseCommand):
    help = "Flush cached diagnostic data for an assistant"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, help="Assistant slug or id")

    def handle(self, *args, **options):
        assistant = resolve_assistant(options["assistant"])
        if not assistant:
            self.stderr.write(self.style.ERROR("Assistant not found"))
            return
        keys = [f"{TRUST_CACHE_PREFIX}{assistant.slug}", f"reflection:{assistant.slug}"]
        removed = 0
        for k in keys:
            if redis_client.delete(k):
                removed += 1
        self.stdout.write(
            self.style.SUCCESS(f"Flushed {removed} cache keys for {assistant.slug}")
        )

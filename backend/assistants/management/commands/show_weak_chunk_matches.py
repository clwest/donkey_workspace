from django.core.management.base import BaseCommand
from assistants.models.thoughts import AssistantThoughtLog
from assistants.models import Assistant
from intel_core.models import Document
from django.db.models import Q


class Command(BaseCommand):
    help = "Show weak chunk match logs for an assistant or document"

    def add_arguments(self, parser):
        parser.add_argument("identifier", help="Assistant slug or document slug")
        parser.add_argument("--limit", type=int, default=10)

    def handle(self, *args, **options):
        ident = options["identifier"]
        limit = options["limit"]
        qs = AssistantThoughtLog.objects.filter(
            fallback_reason__in=["weak_chunks", "summary_fallback"]
        ).order_by("-created_at")
        assistant = Assistant.objects.filter(slug=ident).first()
        if assistant:
            qs = qs.filter(assistant=assistant)
        else:
            doc = Document.objects.filter(slug=ident).first()
            if doc:
                qs = qs.filter(fallback_details__document_id=str(doc.id))
        self.stdout.write(f"Showing last {limit} weak matches for {ident}")
        for log in qs[:limit]:
            details = log.fallback_details or {}
            ids = details.get("chunk_ids", [])
            scores = details.get("scores", [])
            pair_str = ", ".join(f"{i}:{s}" for i, s in zip(ids, scores))
            self.stdout.write(f"{log.created_at:%Y-%m-%d %H:%M} | {pair_str}")


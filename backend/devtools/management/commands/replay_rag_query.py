from django.core.management.base import BaseCommand
from assistants.models import Assistant
from assistants.utils.chunk_retriever import get_relevant_chunks
from utils.rag_diagnostic import log_rag_diagnostic
import json

class Command(BaseCommand):
    help = "Replay a query through RAG retrieval and log diagnostics"

    def add_arguments(self, parser):
        parser.add_argument("--query", required=True)
        parser.add_argument(
            "--assistant",
            default="zeno-the-build-wizard",
            help="Assistant slug (defaults to 'zeno-the-build-wizard')",
        )

    def handle(self, *args, **options):
        query = options["query"]
        slug = options["assistant"]
        try:
            assistant = Assistant.objects.get(slug=slug)
        except Assistant.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    f"❌ Assistant '{slug}' not found. Try running 'python manage.py seed_dev_assistant' or pass a valid slug."
                )
            )
            return
        (chunks, reason, fallback, glossary_present, top_score, _cid, gf, ff, ft, debug) = get_relevant_chunks(
            str(assistant.id),
            query,
            memory_context_id=str(assistant.memory_context_id) if assistant.memory_context_id else None,
            debug=True,
            log_diagnostic=True,
        )
        rag_meta = {
            "used_chunks": chunks,
            "rag_fallback": fallback,
            "anchor_hits": [c.get("anchor_slug") for c in chunks if c.get("anchor_slug")],
            "retrieval_score": top_score,
            "fallback_reason": reason,
            **debug,
        }
        log = log_rag_diagnostic(
            assistant,
            query,
            rag_meta,
            memory_context_id=str(assistant.memory_context_id) if assistant.memory_context_id else None,
        )
        self.stdout.write(json.dumps({"log": log.id, "chunks": chunks}, indent=2))

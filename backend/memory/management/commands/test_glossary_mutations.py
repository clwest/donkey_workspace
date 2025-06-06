from django.core.management.base import BaseCommand
from assistants.models import Assistant
from assistants.utils.chunk_retriever import get_rag_chunk_debug
from memory.models import SymbolicMemoryAnchor


def run_glossary_mutation_tests(slug, stdout=None):
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        if stdout:
            stdout.write(f"Assistant '{slug}' not found")
        return []

    anchors = SymbolicMemoryAnchor.objects.filter(
        assistant=assistant, suggested_label__isnull=False
    )
    results = []
    for anchor in anchors:
        before = get_rag_chunk_debug(str(assistant.id), anchor.label)
        after = get_rag_chunk_debug(str(assistant.id), anchor.suggested_label)
        score_before = before.get("retrieval_score") or 0.0
        score_after = after.get("retrieval_score") or 0.0
        fb_before = 1 if before.get("fallback_triggered") else 0
        fb_after = 1 if after.get("fallback_triggered") else 0
        anchor.mutation_score_before = score_before * (1 - fb_before)
        anchor.mutation_score_after = score_after * (1 - fb_after)
        anchor.save(update_fields=[
            "mutation_score_before",
            "mutation_score_after",
            "mutation_score_delta",
        ])
        results.append(
            {
                "anchor": anchor.slug,
                "before": anchor.mutation_score_before,
                "after": anchor.mutation_score_after,
                "delta": anchor.mutation_score_delta,
            }
        )
        if stdout:
            stdout.write(
                f"{anchor.slug}: {anchor.mutation_score_before:.2f} -> {anchor.mutation_score_after:.2f} ({anchor.mutation_score_delta:+.2f})"
            )
    return results


class Command(BaseCommand):
    help = "Run RAG tests for glossary mutations"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)

    def handle(self, *args, **options):
        slug = options["assistant"]
        run_glossary_mutation_tests(slug, stdout=self.stdout)

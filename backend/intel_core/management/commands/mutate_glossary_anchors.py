import json
from typing import List

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from assistants.models import Assistant
from assistants.utils.chunk_retriever import get_glossary_terms_from_reflections
from memory.models import SymbolicMemoryAnchor, GlossaryChangeEvent
from intel_core.utils.anchor_mutation import suggest_anchor_mutations


class Command(BaseCommand):
    """Suggest or apply glossary anchor mutations based on RAG logs."""

    help = "Suggest mutated glossary anchors from diagnostics"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, type=str)
        parser.add_argument("--from-json", dest="from_json", required=True)
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--save-to-review", action="store_true")

    def handle(self, *args, **options):
        slug = options["assistant"]
        json_path = options["from_json"]
        apply_changes = options.get("apply")
        save_review = options.get("save_to_review")

        try:
            assistant = Assistant.objects.get(slug=slug)
        except Assistant.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
            return

        with open(json_path, "r") as f:
            data = json.load(f)

        record = next((r for r in data if r.get("assistant") == slug), None)
        if not record or not record.get("issues"):
            self.stdout.write("No failed anchors found in diagnostic file.")
            return

        failed: List[str] = record["issues"]
        context_id = str(assistant.memory_context_id) if assistant.memory_context_id else None
        reflections = get_glossary_terms_from_reflections(context_id)
        context_text = ", ".join(reflections)

        for term in failed:
            self.stdout.write(self.style.WARNING(f"\n⚠️ Anchor miss: {term}"))
            suggestion = suggest_anchor_mutations(term, context_text)
            self.stdout.write(suggestion)

            anchors = [s.strip("- •\n") for s in suggestion.splitlines() if s.strip()]

            if apply_changes:
                for a in anchors:
                    if not a:
                        continue
                    slug_a = slugify(a)
                    obj, created = SymbolicMemoryAnchor.objects.get_or_create(
                        slug=slug_a,
                        defaults={
                            "label": a.title(),
                            "source": "mutation",
                            "created_from": "mutation",
                            "mutation_source": "codex_synonym",
                        },
                    )
                    obj.reinforced_by.add(assistant)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Added anchor {slug_a}"))
                    else:
                        self.stdout.write(f"Existing anchor {slug_a} updated")

            if save_review:
                for a in anchors:
                    if a:
                        GlossaryChangeEvent.objects.create(term=a, boost=0.0)
                        self.stdout.write(f"Queued {a} for review")

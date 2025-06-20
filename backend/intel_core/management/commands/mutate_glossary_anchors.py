import json
import os
from typing import List

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from assistants.utils.resolve import resolve_assistant
from assistants.utils.chunk_retriever import get_glossary_terms_from_reflections
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog
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

        assistant = resolve_assistant(slug)
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
            return

        if not os.path.exists(json_path):
            self.stderr.write(self.style.ERROR(f"File '{json_path}' not found"))
            return

        try:
            with open(json_path, "r") as f:
                raw_content = f.read().strip()
                if not raw_content:
                    self.stderr.write(self.style.ERROR(f"File '{json_path}' is empty"))
                    return
                data = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            self.stderr.write(
                self.style.ERROR(f"Failed to parse '{json_path}': {exc.msg}")
            )
            return

        record = next((r for r in data if r.get("assistant") == slug), None)
        if not record or not record.get("issues"):
            self.stdout.write("No failed anchors found in diagnostic file.")
            return

        failed: List[str] = record["issues"]
        context_id = (
            str(assistant.memory_context_id) if assistant.memory_context_id else None
        )
        reflections = get_glossary_terms_from_reflections(context_id)
        context_text = ", ".join(reflections)

        for term in failed:
            self.stdout.write(self.style.WARNING(f"\n⚠️ Anchor miss: {term}"))
            suggestion = suggest_anchor_mutations(term, context_text)
            self.stdout.write(suggestion)

            anchors = []
            for line in suggestion.splitlines():
                cleaned = line.strip().lstrip("- •")
                if not cleaned:
                    continue
                if cleaned[0].isdigit() and "." in cleaned:
                    cleaned = cleaned.split(".", 1)[1].strip()
                if "\"" in cleaned:
                    parts = cleaned.split("\"")
                    if len(parts) >= 3:
                        cleaned = parts[1]
                if " - " in cleaned:
                    cleaned = cleaned.split(" - ", 1)[0].strip()
                cleaned = cleaned.strip()
                if cleaned:
                    anchors.append(cleaned)

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
                        },
                    )
                    obj.reinforced_by.add(assistant)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Added anchor {slug_a}"))
                    else:
                        self.stdout.write(f"Existing anchor {slug_a} updated")

            if save_review:
                orig_anchor = SymbolicMemoryAnchor.objects.filter(slug=slugify(term)).first()
                log = (
                    RAGGroundingLog.objects.filter(
                        assistant=assistant, expected_anchor=term
                    )
                    .order_by("-created_at")
                    .first()
                )
                score = None
                if log:
                    score = log.corrected_score or log.retrieval_score
                for a in anchors:
                    if not a:
                        continue
                    if SymbolicMemoryAnchor.objects.filter(
                        label__iexact=a, related_anchor=orig_anchor
                    ).exists():
                        self.stdout.write(self.style.WARNING(f"⚠️ Already exists: {a}"))
                        continue
                    slug_a = slugify(a)
                    if SymbolicMemoryAnchor.objects.filter(slug=slug_a).exists():
                        base = slug_a
                        i = 1
                        while SymbolicMemoryAnchor.objects.filter(slug=f"{base}-{i}").exists():
                            i += 1
                        slug_a = f"{base}-{i}"
                    SymbolicMemoryAnchor.objects.create(
                        slug=slug_a,
                        label=a,
                        mutation_source="rag_auto_suggest",
                        mutation_status="pending",
                        related_anchor=orig_anchor,
                        suggested_by="gpt-4o",
                        assistant=assistant,
                        memory_context=assistant.memory_context,
                        fallback_score=score,
                        retrieved_from="RAGGroundingLog",
                        source="mutation",
                        created_from="mutation",
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Saved: {a} (source: rag_auto_suggest)")
                    )

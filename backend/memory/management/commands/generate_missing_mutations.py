from django.core.management.base import BaseCommand
from memory.models import SymbolicMemoryAnchor
from intel_core.models import GlossaryFallbackReflectionLog
from utils.llm import call_gpt4
from assistants.utils.resolve import resolve_assistant
import logging

logger = logging.getLogger(__name__)


def generate_missing_mutations_for_assistant(slug, stdout=None):
    anchors_qs = SymbolicMemoryAnchor.objects.filter(
        mutation_status="pending",
        suggested_label__isnull=True,
        assistant__slug=slug,
    )
    stats = {
        "total": anchors_qs.count(),
        "skipped": 0,
        "fallback_positive": 0,
        "created": {},
    }
    updated = []

    for anchor in anchors_qs:
        if anchor is None or anchor.fallback_score is None:
            stats["skipped"] += 1
            if stdout:
                stdout.write(
                    f"⚠️ Skipping malformed anchor {getattr(anchor, 'slug', 'unknown')}"
                )
            continue

        if anchor.fallback_score > 0:
            stats["fallback_positive"] += 1

        fallback_count = GlossaryFallbackReflectionLog.objects.filter(
            anchor_slug=anchor.slug
        ).count()

        if stdout:
            stdout.write(
                f"🧪 Checking: {anchor.label} | fallback_score={anchor.fallback_score} | fallback_count={fallback_count}"
            )
            prompt = (
                f'The assistant failed to ground the term "{anchor.label}" in recent memory. '
                'Suggest a clearer or more precise replacement term. Avoid explanations. Keep it under 3 words.'
            )
            try:
                suggestion = call_gpt4(prompt)

                cleaned = suggestion.strip().strip('"').strip(".")
                if cleaned:
                    anchor.suggested_label = cleaned
                    anchor.save(update_fields=["suggested_label"])
                    updated.append((anchor.label, cleaned))
                    stats["created"].setdefault(anchor.mutation_source or "unknown", 0)
                    stats["created"][anchor.mutation_source or "unknown"] += 1
                    if stdout:
                        stdout.write(f"💡 {anchor.label} → {cleaned}")
                else:
                    if stdout:
                        stdout.write(f"⚠️ Empty suggestion for {anchor.label} — skipping.")
            except Exception as exc:
                if stdout:
                    stdout.write(f"❌ GPT error for {anchor.label}: {exc}")
                logger.exception("GPT suggestion failed for %s", anchor.slug)
            
    if stdout:
        if updated:
            stdout.write(f"✅ Updated {len(updated)} anchors:")
            for orig, sug in updated:
                stdout.write(f"- {orig} → {sug}")
        else:
            stdout.write("No anchors updated.")

    return updated, stats


class Command(BaseCommand):
    help = "Generate missing glossary mutation suggestions"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)

    def handle(self, *args, **options):
        slug = options["assistant"]
        assistant = resolve_assistant(slug)
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
            return
        generate_missing_mutations_for_assistant(assistant.slug, stdout=self.stdout)

from django.core.management.base import BaseCommand
from memory.models import SymbolicMemoryAnchor
from intel_core.models import GlossaryFallbackReflectionLog
from utils.llm import call_gpt4


def generate_missing_mutations_for_assistant(slug, stdout=None):
    anchors = SymbolicMemoryAnchor.objects.filter(
        mutation_status="pending",
        suggested_label__isnull=True,
        assistant__slug=slug,
    )
    updated = []

    for anchor in anchors:
        
        fallback_count = GlossaryFallbackReflectionLog.objects.filter(
            anchor_slug=anchor.slug
        ).count()

        if True:
            stdout.write(f"🧪 Checking: {anchor.label} | fallback_score={anchor.fallback_score} | fallback_count={fallback_count}")
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
                    if stdout:
                        stdout.write(f"💡 {anchor.label} → {cleaned}")
                else:
                    if stdout:
                        stdout.write(f"⚠️ Empty suggestion for {anchor.label} — skipping.")
            except Exception as exc:
                if stdout:
                    stdout.write(f"❌ GPT error for {anchor.label}: {exc}")
            
    if stdout:
        if updated:
            stdout.write(f"✅ Updated {len(updated)} anchors:")
            for orig, sug in updated:
                stdout.write(f"- {orig} → {sug}")
        else:
            stdout.write("No anchors updated.")

    return updated


class Command(BaseCommand):
    help = "Generate missing glossary mutation suggestions"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)

    def handle(self, *args, **options):
        slug = options["assistant"]
        generate_missing_mutations_for_assistant(slug, stdout=self.stdout)
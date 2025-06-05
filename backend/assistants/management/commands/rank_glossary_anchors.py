from django.core.management.base import BaseCommand
from assistants.models import Assistant
import json
from collections import Counter

class Command(BaseCommand):
    """Rank glossary anchors from RAG diagnostics JSON file or database."""

    help = "Score glossary anchors by hits/fallbacks using diagnostic output"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, type=str, help="Assistant slug")
        parser.add_argument("--from-json", dest="from_json", help="Path to diagnostics JSON file")

    def handle(self, *args, **options):
        slug = options["assistant"]
        json_path = options["from_json"]

        try:
            assistant = Assistant.objects.get(slug=slug)
        except Assistant.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
            return

        if not json_path:
            self.stderr.write("❌ Must use --from-json to provide diagnostic file.")
            return

        with open(json_path, "r") as f:
            data = json.load(f)

        # Find the assistant's diagnostic blob
        record = next((r for r in data if r.get("assistant") == slug), None)
        if not record or "issues" not in record:
            self.stderr.write(f"⚠️ No issues found in diagnostic file for assistant '{slug}'")
            return

        issues = record["issues"]
        freq = Counter(issues)

        self.stdout.write(f"\n📊 Glossary Fallback Frequency — Assistant: {slug}")
        self.stdout.write("-" * 60)
        self.stdout.write(f"{'Anchor':<30} {'Fallbacks':<10}")
        self.stdout.write("-" * 60)

        for term, count in freq.most_common(50):
            self.stdout.write(f"{term:<30} {count:<10}")
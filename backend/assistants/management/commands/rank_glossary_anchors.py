from django.core.management.base import BaseCommand
import json
from collections import Counter
from assistants.models import Assistant
import unicodedata


class Command(BaseCommand):
    """Rank glossary anchors from RAG diagnostics JSON file or database."""

    help = "Score glossary anchors by hits/fallbacks using diagnostic output"

    def add_arguments(self, parser):
        parser.add_argument(
            "--assistant",
            required=True,
            type=str,
            help="Assistant slug",
        )
        parser.add_argument(
            "--from-json",
            dest="from_json",
            help="Path to diagnostics JSON file",
        )

    def handle(self, *args, **options):
        identifier = options["assistant"]
        json_path = options["from_json"]

        def normalize_slug(text):
            slug_text = unicodedata.normalize("NFKD", text)
            ascii_text = slug_text.encode("ascii", "ignore").decode()
            return ascii_text.lower()

        normalized_id = normalize_slug(identifier)

        assistant = (
            Assistant.objects.filter(slug=identifier).first() or
            Assistant.objects.filter(slug=normalized_id).first() or
            Assistant.objects.filter(name__icontains=identifier).first()
        )

        if not assistant:
            err = (
                "Assistant '{id}' not found — tried slug, normalized slug, "
                "and fallback name match"
            ).format(id=identifier)
            self.stderr.write(self.style.ERROR(err))
            return

        slug = assistant.slug

        if not json_path:
            msg = "❌ Must use --from-json to provide diagnostic file."
            self.stderr.write(msg)
            return

        with open(json_path, "r") as f:
            data = json.load(f)

        # Determine the correct record structure (list vs single dict)
        record = None
        if isinstance(data, list):
            record = next(
                (
                    r
                    for r in data
                    if isinstance(r, dict) and r.get("assistant") == slug
                ),
                None,
            )
        elif isinstance(data, dict):
            if data.get("assistant"):
                if data.get("assistant") == slug:
                    record = data
            else:
                for key in ("results", "diagnostics", "records", "items"):
                    sub = data.get(key)
                    if isinstance(sub, list):
                        record = next(
                            (
                                r
                                for r in sub
                                if isinstance(r, dict)
                                and r.get("assistant") == slug
                            ),
                            None,
                        )
                        if record:
                            break

        if not record:
            msg = (
                "⚠️ No matching assistant data found in diagnostic file for "
                f"'{slug}'"
            )
            self.stderr.write(msg)
            return

        if "issues" in record:
            freq = Counter(record["issues"])
        elif "results" in record:
            freq = Counter()
            for row in record.get("results", []):
                if not isinstance(row, dict):
                    continue
                anchor = row.get("anchor")
                if not anchor:
                    continue
                fallbacks = row.get("fallbacks")
                if fallbacks is not None:
                    freq[anchor] += fallbacks
                elif row.get("status") in {"fallback", "miss"}:
                    freq[anchor] += 1
        else:
            msg = (
                "⚠️ No issues or results found in diagnostic file for "
                f"assistant '{slug}'"
            )
            self.stderr.write(msg)
            return

        header = f"\n📊 Glossary Fallback Frequency — Assistant: {slug}"
        self.stdout.write(header)
        self.stdout.write("-" * 60)
        self.stdout.write(f"{'Anchor':<30} {'Fallbacks':<10}")
        self.stdout.write("-" * 60)

        for term, count in freq.most_common(50):
            self.stdout.write(f"{term:<30} {count:<10}")

from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.models import RAGGroundingLog
import json

class Command(BaseCommand):
    """Rank glossary anchors based on hits and fallback logs."""

    help = "Rank glossary anchors from RAGGroundingLog data"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, type=str)
        parser.add_argument("--from-json", dest="from_json")

    def handle(self, *args, **options):
        slug = options["assistant"]
        try:
            assistant = Assistant.objects.get(slug=slug)
        except Assistant.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
            return

        records = []
        if options.get("from_json"):
            with open(options["from_json"], "r") as f:
                records = json.load(f)
        else:
            qs = RAGGroundingLog.objects.filter(assistant=assistant)
            for log in qs:
                records.append({
                    "anchor": log.expected_anchor or "prompt",
                    "fallback": log.fallback_triggered,
                    "score": log.corrected_score or log.retrieval_score,
                    "boost_type": log.glossary_boost_type,
                })

        stats = {}
        for r in records:
            anchor = r.get("anchor") or "prompt"
            s = stats.setdefault(anchor, {"hits":0, "fallbacks":0, "scores":[], "boost_type":r.get("boost_type")})
            if r.get("fallback"):
                s["fallbacks"] += 1
            else:
                s["hits"] += 1
            if r.get("score") is not None:
                s["scores"].append(r["score"])
            if not s.get("boost_type"):
                s["boost_type"] = r.get("boost_type")

        headers = ["Anchor", "Hits", "Fallbacks", "Avg Score", "Boost Type"]
        self.stdout.write("\t".join(headers))
        for anchor, info in stats.items():
            avg = sum(info["scores"])/len(info["scores"]) if info["scores"] else 0.0
            line = [anchor, str(info["hits"]), str(info["fallbacks"]), f"{avg:.2f}", info.get("boost_type") or "None"]
            self.stdout.write("\t".join(line))


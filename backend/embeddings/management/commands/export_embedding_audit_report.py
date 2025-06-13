import json
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from embeddings.models import Embedding
from memory.models import MemoryEntry
from intel_core.models import DocumentChunk
from prompts.models import Prompt
from mcp_core.models import DevDoc


class Command(BaseCommand):
    help = "Export a markdown summary of embedding health"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="embedding_audit_report.md",
            help="File path to write report",
        )

    def handle(self, *args, **options):
        output = options["output"]
        ct_memory = ContentType.objects.get_for_model(MemoryEntry)
        ct_chunk = ContentType.objects.get_for_model(DocumentChunk)
        ct_prompt = ContentType.objects.get_for_model(Prompt)
        ct_devdoc = ContentType.objects.get_for_model(DevDoc)
        allowed = {ct_memory.id, ct_chunk.id, ct_prompt.id, ct_devdoc.id}

        stats = {}
        missing_meta = 0
        for emb in Embedding.objects.select_related("content_type"):
            if emb.content_type_id not in allowed:
                continue
            model = emb.content_type.model
            entry = stats.setdefault(model, {"total": 0, "mismatched": 0, "orphans": 0})
            entry["total"] += 1
            obj = emb.content_object
            if obj is None:
                entry["orphans"] += 1
                continue
            expected_ct = ContentType.objects.get_for_model(obj.__class__)
            expected_oid = str(obj.id)
            expected_cid = f"{expected_ct.model}:{obj.id}"
            if (
                emb.content_type_id != expected_ct.id
                or str(emb.object_id) != expected_oid
                or emb.content_id != expected_cid
            ):
                entry["mismatched"] += 1
            if not emb.session_id or not emb.source_type:
                missing_meta += 1

        lines = [
            "# Embedding Audit Report",
            "",
            "| Model | Total | Mismatched | Orphans |",
            "|-------|-------|-----------|---------|",
        ]
        for model, row in stats.items():
            lines.append(
                f"| {model} | {row['total']} | {row['mismatched']} | {row['orphans']} |"
            )
        lines.append("")
        lines.append(f"Missing metadata count: {missing_meta}")

        with open(output, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        self.stdout.write(self.style.SUCCESS(f"Report written to {output}"))

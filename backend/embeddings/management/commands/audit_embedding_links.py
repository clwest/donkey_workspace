from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
import json

from embeddings.models import Embedding, EmbeddingDebugTag
from memory.models import MemoryEntry
from intel_core.models import DocumentChunk
from prompts.models import Prompt


class Command(BaseCommand):
    help = "Audit embeddings for content link consistency"

    def add_arguments(self, parser):
        parser.add_argument(
            "--export",
            help="Path to export mismatched rows as JSON",
            default=None,
        )
        parser.add_argument(
            "--diff",
            action="store_true",
            help="Show per-field mismatch details",
        )

    def handle(self, *args, **options):
        ct_memory = ContentType.objects.get_for_model(MemoryEntry)
        ct_chunk = ContentType.objects.get_for_model(DocumentChunk)
        ct_prompt = ContentType.objects.get_for_model(Prompt)
        allowed = {ct_memory.id, ct_chunk.id, ct_prompt.id}

        mismatches = []
        matched = 0
        mismatched = 0
        orphans = 0
        total = Embedding.objects.count()

        for emb in Embedding.objects.select_related("content_type"):
            ct = emb.content_type
            obj = emb.content_object

            if not ct or ct.id not in allowed:
                # Skip embeddings from unsupported models
                continue

            if obj is None:
                orphans += 1
                mismatches.append(
                    {
                        "id": str(emb.id),
                        "reason": "orphan",
                        "is_orphan": True,
                        "content_type": ct.model if ct else None,
                        "object_id": emb.object_id,
                        "content_id": emb.content_id,
                    }
                )
                EmbeddingDebugTag.objects.create(
                    embedding=emb,
                    reason="missing chunk" if ct == ct_chunk else "orphaned-object",
                )
                continue

            expected_ct = ContentType.objects.get_for_model(obj.__class__)
            expected_oid = str(obj.id)
            expected_cid = f"{expected_ct.model}:{obj.id}"

            actual_ct = emb.content_type_id
            actual_oid = str(emb.object_id)
            actual_cid = emb.content_id

            if (
                actual_ct != expected_ct.id
                or actual_oid != expected_oid
                or actual_cid != expected_cid
            ):
                mismatched += 1
                mismatches.append(
                    {
                        "id": str(emb.id),
                        "is_orphan": False,
                        "actual_ct": actual_ct,
                        "expected_ct": expected_ct.id,
                        "actual_oid": actual_oid,
                        "expected_oid": expected_oid,
                        "actual_cid": actual_cid,
                        "expected_cid": expected_cid,
                    }
                )
                reason = "wrong FK"
                if ":" not in actual_cid:
                    reason = "bad format"
                EmbeddingDebugTag.objects.create(
                    embedding=emb,
                    reason=reason,
                )
            else:
                matched += 1

        diff = options.get("diff")

        self.stdout.write(f"Embeddings scanned: {total}")
        self.stdout.write(f"Matched: {matched}")
        self.stdout.write(f"Mismatched: {mismatched}")
        self.stdout.write(f"Orphans: {orphans}")

        export = options.get("export")
        if export:
            with open(export, "w", encoding="utf-8") as fh:
                json.dump(mismatches, fh, indent=2)
            self.stdout.write(f"Exported details to {export}")

        if diff:
            for m in mismatches:
                if m.get("reason") == "orphan":
                    self.stdout.write(f"\n❌ Orphan: Embedding {m['id']}")
                    self.stdout.write(
                        f"   content_type: {m.get('content_type')} object_id: {m.get('object_id')} content_id: {m.get('content_id')}"
                    )
                else:
                    self.stdout.write(f"\n❌ Mismatch: Embedding {m['id']}")
                    self.stdout.write(
                        f"   content_type:    actual={m['actual_ct']}  expected={m['expected_ct']}"
                    )
                    self.stdout.write(
                        f"   object_id:       actual={m['actual_oid']}  expected={m['expected_oid']}"
                    )
                    self.stdout.write(
                        f"   content_id:      actual={m['actual_cid']}  expected={m['expected_cid']}"
                    )

        return {"matched": matched, "mismatched": mismatched, "orphans": orphans}

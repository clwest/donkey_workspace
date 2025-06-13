from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from embeddings.models import Embedding, EmbeddingDebugTag, EmbeddingDriftLog
from memory.models import MemoryEntry
from intel_core.models import DocumentChunk
from prompts.models import Prompt
from datetime import datetime

class Command(BaseCommand):
    help = "Audit embeddings and record drift metrics"

    def add_arguments(self, parser):
        parser.add_argument("--since", help="Skip if a log exists after this ISO timestamp", default=None)

    def handle(self, *args, **options):
        since = options.get("since")
        if since:
            try:
                ts = datetime.fromisoformat(since)
                if EmbeddingDriftLog.objects.filter(timestamp__gte=ts).exists():
                    self.stdout.write("Log already exists after given timestamp")
                    return
            except ValueError:
                pass

        ct_memory = ContentType.objects.get_for_model(MemoryEntry)
        ct_chunk = ContentType.objects.get_for_model(DocumentChunk)
        ct_prompt = ContentType.objects.get_for_model(Prompt)
        allowed = {ct_memory.id, ct_chunk.id, ct_prompt.id}

        stats = {}
        for emb in Embedding.objects.select_related("content_type"):
            ct = emb.content_type
            obj = emb.content_object
            if not ct or ct.id not in allowed:
                continue
            model = ct.model
            if ct == ct_memory:
                mem = MemoryEntry.objects.filter(id=emb.object_id).first()
                if not mem:
                    continue
                key = (mem.assistant_id, mem.context_id)
            else:
                key = (None, None)

            entry = stats.setdefault(key, {"model": model, "mismatched": 0, "orphans": 0})
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

        repaired_count = EmbeddingDebugTag.objects.filter(repair_status="repaired").count()
        now = timezone.now()
        for (assistant_id, context_id), row in stats.items():
            EmbeddingDriftLog.objects.create(
                timestamp=now,
                model_name=row["model"],
                assistant_id=assistant_id,
                context_id=context_id,
                mismatched_count=row["mismatched"],
                orphaned_count=row["orphans"],
                repaired_count=repaired_count,
            )
        self.stdout.write(f"Logged drift for {len(stats)} contexts")

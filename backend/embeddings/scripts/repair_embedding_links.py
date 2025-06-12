"""Repair malformed embedding content links."""

import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from django.contrib.contenttypes.models import ContentType
from embeddings.models import Embedding
from intel_core.models import DocumentChunk
from prompts.models import Prompt
from memory.models import MemoryEntry


CT_MAP = {
    "documentchunk": ContentType.objects.get_for_model(DocumentChunk),
    "prompt": ContentType.objects.get_for_model(Prompt),
    "memoryentry": ContentType.objects.get_for_model(MemoryEntry),
}


def repair(apply=False):
    fixed = 0
    for emb in Embedding.objects.select_related("content_type"):
        ct = emb.content_type
        obj_id = emb.object_id
        changed = False
        if ct and obj_id:
            expected = f"{ct.model}:{obj_id}"
            if emb.content_id != expected:
                emb.content_id = expected
                changed = True
        elif emb.content_id and ":" in emb.content_id:
            ct_name, obj_id = emb.content_id.split(":", 1)
            ct_new = CT_MAP.get(ct_name)
            if ct_new:
                emb.content_type = ct_new
                emb.object_id = obj_id
                changed = True
        if changed and apply:
            emb.save(update_fields=["content_type", "object_id", "content_id"])
            fixed += 1
    return fixed


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Repair embedding links")
    parser.add_argument("--apply", action="store_true", help="Persist changes")
    args = parser.parse_args()
    count = repair(apply=args.apply)
    print(f"Fixed {count} embeddings")

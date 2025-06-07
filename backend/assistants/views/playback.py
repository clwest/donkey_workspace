from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from assistants.models import Assistant
from memory.models import ReflectionReplayLog, RAGPlaybackLog


@api_view(["GET"])
def rag_playback_compare(request, slug, id):
    """Return comparison between the first and latest playback for a replay."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from uuid import UUID

    replay = get_object_or_404(
        ReflectionReplayLog, id=UUID(str(id)), assistant=assistant
    )
    latest = replay.rag_playback
    if not latest:
        return Response({"detail": "No playback"}, status=404)

    qs = (
        ReflectionReplayLog.objects.filter(
            assistant=assistant, original_reflection=replay.original_reflection
        )
        .exclude(rag_playback=None)
        .order_by("created_at")
    )
    original = qs.first().rag_playback if qs.exists() else latest

    def diff_chunks(old, new):
        old_map = {c["id"]: c for c in old.chunks}
        new_map = {c["id"]: c for c in new.chunks}
        drift = []
        for cid in new_map:
            old_c = old_map.get(cid)
            new_c = new_map[cid]
            if not old_c or new_c.get("final_score") != old_c.get("final_score"):
                drift.append(
                    {
                        "label": ",".join(new_c.get("matched_anchors", [])),
                        "old_score": old_c.get("final_score") if old_c else None,
                        "new_score": new_c.get("final_score"),
                        "matched": bool(new_c.get("matched_anchors")),
                    }
                )
        return drift

    data = {
        "query": latest.query_term or latest.query,
        "score_cutoff": latest.score_cutoff,
        "original_chunks": original.chunks,
        "replay_chunks": latest.chunks,
        "fallback": latest.fallback_reason,
        "anchor_drift": diff_chunks(original, latest),
    }
    return Response(data)

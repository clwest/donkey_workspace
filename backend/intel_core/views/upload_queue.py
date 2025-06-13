from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import uuid

QUEUE_KEY_TEMPLATE = "upload_queue:{user_id}"


def _get_queue(user_id):
    key = QUEUE_KEY_TEMPLATE.format(user_id=user_id)
    return cache.get(key, [])


def _set_queue(user_id, queue):
    key = QUEUE_KEY_TEMPLATE.format(user_id=user_id)
    cache.set(key, queue, timeout=3600)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enqueue_upload(request):
    """Add a document ID to the user's upload queue."""
    doc_id = request.data.get("doc_id")
    if not doc_id:
        return Response({"error": "doc_id required"}, status=400)
    try:
        uuid.UUID(str(doc_id))
    except Exception:
        return Response({"error": "invalid doc_id"}, status=400)
    q = _get_queue(request.user.id)
    if doc_id not in q:
        q.append(str(doc_id))
        _set_queue(request.user.id, q)
    return Response({"queued": q})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def upload_queue_status(request):
    """Return the current upload queue for the user."""
    return Response({"queue": _get_queue(request.user.id)})

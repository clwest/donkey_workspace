from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant, AssistantMessage, ChatSession
from memory.services import MemoryService
from assistants.serializers import AssistantMessageSerializer

@api_view(["POST"])
def send_message(request):
    """Send a message from one assistant to another."""
    sender_slug = request.data.get("sender")
    recipient_slug = request.data.get("recipient")
    content = request.data.get("content")
    session_id = request.data.get("session")
    related_memory_id = request.data.get("related_memory")
    if not (sender_slug and recipient_slug and content):
        return Response({"error": "sender, recipient and content required"}, status=400)
    sender = get_object_or_404(Assistant, slug=sender_slug)
    recipient = get_object_or_404(Assistant, slug=recipient_slug)
    session = None
    if session_id:
        session = ChatSession.objects.filter(session_id=session_id).first()
    related_memory = None
    if related_memory_id:
        related_memory = MemoryService.get_entry(related_memory_id)
    msg = AssistantMessage.objects.create(
        sender=sender,
        recipient=recipient,
        content=content,
        session=session,
        related_memory=related_memory,
    )
    return Response(AssistantMessageSerializer(msg).data, status=201)

@api_view(["GET"])
def inbox(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    msgs = AssistantMessage.objects.filter(recipient=assistant).order_by("-created_at")
    return Response(AssistantMessageSerializer(msgs, many=True).data)

@api_view(["GET"])
def outbox(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    msgs = AssistantMessage.objects.filter(sender=assistant).order_by("-created_at")
    return Response(AssistantMessageSerializer(msgs, many=True).data)


from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import MythgraphNode, AssistantMythgraphDraft
from ..serializers import MythgraphNodeSerializer, AssistantMythgraphDraftSerializer


class MythgraphNodeViewSet(viewsets.ModelViewSet):
    queryset = MythgraphNode.objects.all().order_by("-created_at")
    serializer_class = MythgraphNodeSerializer

    @action(detail=False, url_path=r"assistant/(?P<assistant_id>[^/]+)")
    def by_assistant(self, request, assistant_id=None):
        draft, _ = AssistantMythgraphDraft.objects.get_or_create(assistant_id=assistant_id)
        data = AssistantMythgraphDraftSerializer(draft).data
        return Response(data)

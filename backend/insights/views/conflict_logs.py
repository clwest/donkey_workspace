from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from insights.models import SymbolicAgentInsightLog
from insights.serializers import SymbolicAgentInsightLogSerializer


@api_view(["GET"])
def conflict_log_list(request):
    """Return recent SymbolicAgentInsightLog entries."""
    qs = SymbolicAgentInsightLog.objects.select_related("agent", "document")
    agent_slug = request.GET.get("agent")
    if agent_slug:
        qs = qs.filter(agent__slug=agent_slug)
    logs = qs.order_by("-created_at")
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(logs, request)
    serializer = SymbolicAgentInsightLogSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

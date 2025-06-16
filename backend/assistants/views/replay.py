from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from assistants.models import Assistant
from memory.models import ReplayThreadLog, DriftAnalysisSnapshot
from assistants.serializers import (
    ReplayThreadLogSerializer,
    DriftAnalysisSnapshotSerializer,
)
from django.core.management import call_command


@api_view(["GET"])
def assistant_replay_logs(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    logs = ReplayThreadLog.objects.filter(assistant=assistant).order_by("-created_at")
    return Response(ReplayThreadLogSerializer(logs, many=True).data)


@api_view(["POST"])
def run_symbolic_replay_view(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    call_command("run_symbolic_replay", assistant=assistant.slug)
    latest = ReplayThreadLog.objects.filter(assistant=assistant).first()
    return Response(ReplayThreadLogSerializer(latest).data)


@api_view(["GET"])
def list_all_replay_logs(request):
    logs = ReplayThreadLog.objects.all().order_by("-created_at")[:50]
    return Response(ReplayThreadLogSerializer(logs, many=True).data)


@api_view(["GET"])
def drift_audit_detail(request, id):
    replay = get_object_or_404(ReplayThreadLog, id=id)
    snapshots = DriftAnalysisSnapshot.objects.filter(replay_log=replay)
    data = DriftAnalysisSnapshotSerializer(snapshots, many=True).data
    return Response({"log": ReplayThreadLogSerializer(replay).data, "snapshots": data})

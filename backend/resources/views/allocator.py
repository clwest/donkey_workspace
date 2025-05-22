from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import ResourcePrediction, ResourceBudget


class ResourceAllocatorView(APIView):
    def get(self, request, assistant_id):
        pred = (
            ResourcePrediction.objects.filter(assistant_id=assistant_id)
            .order_by("-prediction_time")
            .first()
        )
        if not pred:
            return Response({"error": "prediction not found"}, status=404)
        return Response(
            {
                "predicted_tokens": pred.predicted_tokens,
                "predicted_compute_ms": pred.predicted_compute_ms,
            }
        )

    def post(self, request, assistant_id):
        allocation = ResourceBudget.objects.create(
            assistant_id=assistant_id,
            allocated_tokens=request.data.get("tokens", 0),
            allocated_compute_ms=request.data.get("compute_ms", 0.0),
        )
        return Response({"budget_id": allocation.id})

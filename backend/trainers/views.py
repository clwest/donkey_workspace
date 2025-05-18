from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import ReplicateModel, ReplicatePrediction
from .serializers import (
    ReplicateModelSerializer,
    ReplicatePredictionSerializer,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated

from .helpers.replicate_helpers import (
    generate_image,
    get_prediction_detail,
    list_prediction_results,
)


class ReplicateModelViewSet(viewsets.ModelViewSet):
    """ViewSet for managing ReplicateModel objects."""

    queryset = ReplicateModel.objects.all()
    serializer_class = ReplicateModelSerializer
    permission_classes = [IsAuthenticated]


class ReplicatePredictionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing ReplicatePrediction objects."""

    queryset = ReplicatePrediction.objects.all()
    serializer_class = ReplicatePredictionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "model"]
    # Disallow unsafe updates/deletes
    http_method_names = ["get", "post", "head", "options"]

    def perform_create(self, serializer):
        # Automatically set the user to the requesting user
        serializer.save(user=self.request.user)


class GeneratePredictionView(APIView):
    """Trigger a new Replicate prediction via POST."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        require_trigger = request.data.get("require_trigger_word", True)
        if not prompt:
            return Response(
                {"detail": "Prompt is required."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        try:
            prediction = generate_image(prompt, require_trigger)
            # Return basic prediction info
            return Response(
                {
                    "id": prediction.id,
                    "status": prediction.status,
                },
                status=http_status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=http_status.HTTP_400_BAD_REQUEST)


class PredictionStatusView(APIView):
    """Retrieve status and details for a given prediction ID."""

    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        data, code = get_prediction_detail(id)
        if data is None:
            return Response({"detail": "Not found."}, status=code)
        # Return prediction status and outputs
        return Response(
            {
                "id": data.id,
                "status": data.status,
                "output": getattr(data, "output", None),
            },
            status=http_status.HTTP_200_OK,
        )


class PredictionListView(APIView):
    """List recent predictions, optionally filtered by status."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_filter = request.query_params.get("status")
        preds = list_prediction_results(status=status_filter)
        items = []
        for p in preds:
            items.append(
                {
                    "id": p.id,
                    "status": p.status,
                    "output": getattr(p, "output", None),
                }
            )
        return Response(items, status=http_status.HTTP_200_OK)

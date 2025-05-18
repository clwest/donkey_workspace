from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    ReplicateModelViewSet,
    ReplicatePredictionViewSet,
    GeneratePredictionView,
    PredictionStatusView,
    PredictionListView,
)

router = DefaultRouter()
router.register(r"models", ReplicateModelViewSet, basename="replicatemodel")
router.register(
    r"predictions", ReplicatePredictionViewSet, basename="replicateprediction"
)

urlpatterns = [
    # Standard CRUD via ViewSets
    path("", include(router.urls)),
    # Custom replicate endpoints
    path(
        "predictions/generate/",
        GeneratePredictionView.as_view(),
        name="prediction-generate",
    ),
    path(
        "predictions/status/<str:id>/",
        PredictionStatusView.as_view(),
        name="prediction-status",
    ),
    path("predictions/list/", PredictionListView.as_view(), name="prediction-list"),
]

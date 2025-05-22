from django.urls import path
from rest_framework.routers import DefaultRouter
from .views.config import SimulationConfigViewSet
from .views.sandbox import SimulationRunView

router = DefaultRouter()
router.register(r"config", SimulationConfigViewSet, basename="simulation-config")

urlpatterns = router.urls + [
    path("run/", SimulationRunView.as_view(), name="simulation-run"),
]

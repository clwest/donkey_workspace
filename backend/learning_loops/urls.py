from django.urls import path
from .views.trigger import AdaptiveLoopTriggerView

urlpatterns = [
    path(
        "trigger/<uuid:assistant_id>/",
        AdaptiveLoopTriggerView.as_view(),
        name="adaptive-loop-trigger",
    ),
]

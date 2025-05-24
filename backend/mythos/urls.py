from django.urls import path
from . import views

urlpatterns = [
    path("assistants/<uuid:assistant_id>/archetype-card/", views.get_archetype_card),
    path("ritual-launchpads/", views.get_ritual_launchpads),
    path("codex/", views.SwarmCodexRootView.as_view(), name="codex-root"),
    path("codex/mutator/<uuid:clause_id>/", views.CodexClauseMutatorView.as_view()),
    path("fault/injector/", views.FaultInjectorView.as_view()),
    path("memory/sandbox/<uuid:assistant_id>/", views.MemoryAlignmentSandboxView.as_view()),
]

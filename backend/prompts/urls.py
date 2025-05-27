import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from .feedback import PromptFeedbackRefinementView
from mcp_core.views import prompts as mcp_prompts

router = DefaultRouter()
router.register(r"capsules", views.PromptCapsuleViewSet, basename="promptcapsule")
router.register(
    r"capsule-transfers", views.CapsuleTransferLogViewSet, basename="capsuletransfer"
)

urlpatterns = [
    # Main prompt list endpoint
    path("", views.list_prompts),
    path("tags/", views.list_prompt_tags),
    path("mutation-styles/", views.list_mutation_styles),
    path("preferences/", views.get_my_prompt_preferences),
    path("preferences/update/", views.update_my_prompt_preferences),
    path("reduce/", views.reduce_prompt),
    path("split/", views.split_prompt),
    path("auto-reduce/", views.auto_reduce_prompt_view),
    path("analyze/", views.analyze_prompt),
    path("mutate-prompt/", views.mutate_prompt_view),
    path("mutate/", views.mutate_prompt_view),
    path("generate-from-idea/", views.generate_prompt_from_idea_view),
    path("create/", views.create_prompt),
    # Prompt templates CRUD
    path(
        "templates/",
        mcp_prompts.list_prompt_templates,
        name="prompt-template-list",
    ),
    path(
        "templates/create/",
        mcp_prompts.create_prompt_template,
        name="prompt-template-create",
    ),
    path(
        "templates/<int:pk>/",
        mcp_prompts.prompt_template_detail,
        name="prompt-template-detail",
    ),
    path(
        "templates/<int:pk>/update/",
        mcp_prompts.update_prompt_template,
        name="prompt-template-update",
    ),
    path(
        "templates/<int:pk>/delete/",
        mcp_prompts.delete_prompt_template,
        name="prompt-template-delete",
    ),
    path("search/", views.prompt_search, name="prompt-search"),
    path("reembed/", views.reembed_all_prompts),
    path("<slug:slug>/update/", views.update_prompt),
    path("<slug:slug>/", views.prompt_detail),
    path("<slug:slug>/assign/", views.assign_prompt_to_assistant),
    path("<slug:slug>/usage-logs/", views.prompt_usage_logs_view),
    path(
        "feedback/prompts/<uuid:prompt_id>/",
        PromptFeedbackRefinementView.as_view(),
        name="prompt-feedback-refinement",
    ),
] + router.urls

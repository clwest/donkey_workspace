import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_prompts),
    path("tags/", views.list_prompt_tags),
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
    path("search/", views.prompt_search, name="prompt-search"),
    path("reembed/", views.reembed_all_prompts),
    path("<slug:slug>/update/", views.update_prompt),
    path("<slug:slug>/", views.prompt_detail),
    path("<slug:slug>/assign/", views.assign_prompt_to_assistant),
    path("<slug:slug>/usage-logs/", views.prompt_usage_logs_view),
]

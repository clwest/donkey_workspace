from django.urls import path
from . import views
from assistants.views import empathy

urlpatterns = [
    path("save/", views.save_memory, name="save_memory"),
    path("recent/", views.recent_memories, name="recent_memories"),
    path("list/", views.list_memories, name="list_memories"),
    path("reflect/", views.reflect_on_memory, name="reflect-on-memory"),
    path("chains/create/", views.create_memory_chain, name="create_memory_chain"),
    path("chains/<uuid:pk>/", views.get_memory_chain, name="get_memory_chain"),
    path("chains/list/", views.list_memory_chains, name="list_memory_chains"),
    path("reflect-on-memories/", views.reflect_on_memories, name="reflect_on_memories"),
    path("reflection/", views.save_reflection, name="save-reflection"),
    path("upload-voice/", views.upload_voice_clip, name="upload_voice_clip"),
    path(
        "memory/<uuid:memory_id>/feedback/",
        views.list_memory_feedback,
        name="memory-feedback-list",
    ),
    path(
        "memory/feedback/submit/",
        views.submit_memory_feedback,
        name="memory-feedback-submit",
    ),
    path("<uuid:id>/mutate/", views.mutate_memory, name="mutate-memory"),
    path("<uuid:id>/", views.memory_detail, name="memory_detail"),
    path("<uuid:memory_id>/bookmark/", views.bookmark_memory, name="bookmark_memory"),
    path(
        "<uuid:memory_id>/unbookmark/",
        views.unbookmark_memory,
        name="unbookmark_memory",
    ),
    path("bookmarked/", views.bookmarked_memories, name="bookmarked_memories"),
    path("by-tag/<slug:slug>/", views.memories_by_tag),
    path("update-tags/<uuid:id>/", views.update_memory_tags),
    path("replace/<uuid:id>/", views.replace_memory),
    path("vector/", views.vector_memories, name="vector-memories"),
    path("<uuid:id>/resonance/", empathy.memory_resonance, name="memory-resonance"),
]

import warnings

warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from . import views

urlpatterns = [
    path("index/", views.tool_index, name="tool-index"),
    path("", views.tool_list, name="tool-list"),
    path("<int:pk>/", views.tool_detail, name="tool-detail"),
    path("<int:pk>/execute/", views.execute_tool_view, name="tool-execute"),
    path("<int:pk>/logs/", views.tool_logs, name="tool-logs"),
    path("<int:pk>/reflections/", views.tool_reflections, name="tool-reflections"),
    path("<int:pk>/reflect/", views.reflect_on_tool_now, name="tool-reflect"),
    path("<slug:slug>/invoke/", views.invoke_tool, name="invoke-tool"),
    path("feedback/<int:id>/", views.submit_tool_feedback, name="tool-feedback"),
]

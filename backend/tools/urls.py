import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from . import views

urlpatterns = [
    path("", views.tool_list, name="tool-list"),
    path("<slug:slug>/invoke/", views.invoke_tool, name="invoke-tool"),
    path("feedback/<int:id>/", views.submit_tool_feedback, name="tool-feedback"),
]

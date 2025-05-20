from django.urls import path
from . import views

urlpatterns = [
    path("", views.tool_list, name="tool-list"),
    path("<slug:slug>/invoke/", views.invoke_tool, name="invoke-tool"),
]

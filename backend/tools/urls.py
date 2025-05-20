from django.urls import path
from . import views

urlpatterns = [
    path("<slug:slug>/invoke/", views.invoke_tool, name="invoke-tool"),
]

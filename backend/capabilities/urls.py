from django.urls import path
from .views import capability_status, capability_status_view

urlpatterns = [
    path("status/", capability_status),
    path("status/simple/", capability_status_view),
]

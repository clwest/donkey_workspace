from django.urls import path
from .views import capability_status

urlpatterns = [
    path("status/", capability_status),
]

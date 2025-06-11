from django.urls import path
from .views import conflict_log_list

urlpatterns = [
    path("conflict_logs/", conflict_log_list, name="conflict-log-list"),
]

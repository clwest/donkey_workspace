import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from . import views

urlpatterns = [
    path("", views.shared_memory_pools, name="shared-memory-pools"),
    path(
        "<uuid:pool_id>/",
        views.shared_memory_pool_detail,
        name="shared-memory-pool-detail",
    ),
    path(
        "<uuid:pool_id>/entries/",
        views.shared_memory_pool_entries,
        name="shared-memory-pool-entries",
    ),
]

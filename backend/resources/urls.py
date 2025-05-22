import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views.allocator import ResourceAllocatorView

urlpatterns = [
    path("predict/<uuid:assistant_id>/", ResourceAllocatorView.as_view()),
    path("allocate/<uuid:assistant_id>/", ResourceAllocatorView.as_view()),
]

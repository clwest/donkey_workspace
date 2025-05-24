import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views import import_view

urlpatterns = [
    path("import/", import_view.DocumentImportView.as_view(), name="document-import"),
    path(
        "upload-status/<uuid:session_id>/",
        import_view.UploadStatusView.as_view(),
        name="document-upload-status",
    ),
]

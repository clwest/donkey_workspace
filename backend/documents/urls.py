from django.urls import path
from .views import import_view

urlpatterns = [
    path("import/", import_view.DocumentImportView.as_view(), name="document-import"),
]

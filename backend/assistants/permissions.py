from rest_framework import permissions
from assistants.models import Assistant

class IsAssistantOwnerOrDemo(permissions.BasePermission):
    """Allow access if assistant is demo or owned by the user."""

    def has_object_permission(self, request, view, obj: Assistant) -> bool:
        if obj.is_demo:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return obj.created_by_id == request.user.id

    def has_permission(self, request, view) -> bool:
        slug = view.kwargs.get("slug")
        if not slug:
            return False
        try:
            assistant = Assistant.objects.get(slug=slug)
        except Assistant.DoesNotExist:
            return False
        return self.has_object_permission(request, view, assistant)

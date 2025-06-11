from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access only to the object's owner or admins."""

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or request.user.is_staff


class AdminOnly(permissions.BasePermission):
    """Allow access only to admin/staff users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

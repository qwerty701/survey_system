from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.authors == request.user or request.user.is_staff

from rest_framework import permissions

class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.authors == request.user:
            return True
        elif request.method == permissions.SAFE_METHODS:
            return False
        else:
            return False


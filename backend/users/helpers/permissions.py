from rest_framework.permissions import BasePermission

class IsModeratorOrAdmin(BasePermission):
    """
    Allows access only to moderators or admin users.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['moderator', 'admin']

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'admin'

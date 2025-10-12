from rest_framework import permissions


class AllowUnauthenticatedUser(permissions.BasePermission):
    """
    Custom permission to only allow unauthenticated users to access
    the reset password view.
    """

    def has_permission(self, request, view):
        # Allow access only if the user is not authenticated
        return not request.user.is_authenticated

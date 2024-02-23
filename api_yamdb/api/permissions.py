# cats/permissions.py

from rest_framework import permissions


def check_admin(request):
    if request.user.is_authenticated:
        return request.user.role == 'admin' or request.user.is_superuser


def check_safe_methods(request):
    if request.method in permissions.SAFE_METHODS:
        return True


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not check_safe_methods(request):
            return check_admin(request)
        return True



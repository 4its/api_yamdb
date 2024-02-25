from rest_framework import permissions, exceptions


def check_admin(request):
    if request.user.is_authenticated:
        return request.user.role == 'admin' or request.user.is_superuser


def check_safe_methods(request):
    return request.method in permissions.SAFE_METHODS


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not check_safe_methods(request):
            return check_admin(request)
        return True


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return check_admin(request)


class CategoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return check_safe_methods(request) or check_admin(request)

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'PUT', 'PATCH'):
            raise exceptions.MethodNotAllowed(request.method)
        return check_admin(request)

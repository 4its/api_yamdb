from rest_framework import permissions, exceptions


def check_safe_methods(request):
    return request.method in permissions.SAFE_METHODS


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if check_safe_methods(request):
            return True
        if request.user.is_authenticated:
            return request.user.is_admin


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin


class IsAuthorAdminModeratorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if check_safe_methods(request):
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if check_safe_methods(request):
            return True
        return (
                request.user.is_authenticated
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator
        )

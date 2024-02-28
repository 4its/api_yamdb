from rest_framework import permissions, exceptions


def check_safe_methods(request):
    return request.method in permissions.SAFE_METHODS


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if check_safe_methods(request):
            return True
        if request.user.is_authenticated:
            return request.user.is_admin


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешает действия с reviews автору, модератору и админу."""

    def has_permission(self, request, view):
        """Проверяет права пользователя на запрос."""
        if check_safe_methods(request):
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Проверяет права пользователя на объект."""
        return obj.author == request.user or check_safe_methods(request)


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin


class IsAdminOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
                check_safe_methods(request)
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator
        )

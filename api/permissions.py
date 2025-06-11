from rest_framework import permissions


class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешаем GET, HEAD, OPTIONS для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для остальных методов только суперпользователь
        return request.user and request.user.is_superuser

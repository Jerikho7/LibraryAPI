from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsReader(BasePermission):
    """Права доступа только для читателя (группа 'readers')."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="readers").exists()


class IsLibrarian(BasePermission):
    """Права доступа только для библиотекаря (группа 'librarians')."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="librarians").exists()


class IsModerator(BasePermission):
    """Права доступа только для модератора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="moderators").exists()


class IsLibrarianOrReadOnly(BasePermission):
    """
    Чтение (GET, HEAD, OPTIONS) доступно всем авторизованным пользователям.
    Модификация — только библиотекарям.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.groups.filter(name="librarians").exists()

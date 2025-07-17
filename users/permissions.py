from rest_framework.permissions import BasePermission

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


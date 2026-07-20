from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, входит ли пользователь в группу модераторов."""

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False

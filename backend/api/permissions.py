from rest_framework import permissions

MESSAGE_NO_PERMISSION = "У вас нет прав для выполнения этого действия."


class IsAuthAdminAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет администраторам и авторам
    выполнять любые действия, а обычным пользователям — только чтение.
    """
    message = MESSAGE_NO_PERMISSION

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or getattr(obj, "username", None) == request.user.username
            or getattr(obj, "author", None) == request.user
        )

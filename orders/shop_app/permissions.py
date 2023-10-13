from rest_framework import permissions

class IsShop(permissions.BasePermission):
    """
    Пользовательское разрешение, чтобы проверить, является ли пользователь магазином
    """
    def has_permission(self, request, view):
        return request.user.type == 'shop'
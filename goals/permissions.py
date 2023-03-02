from rest_framework import permissions

from goals.models import BoardParticipant


class BoardPermissions(permissions.BasePermission):
    """
    Возвращает False, если у пользователя нет доступа или пользователь не авторизован.
    Если метод запроса входит в SAFE_METHODS (т.е. не меняет данные), то проверяем существование пользователя у доски.
    Если метод запроса не входит в SAFE_METHODS, то проверяем, что пользователь является создателем доски.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj
            ).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj, role=BoardParticipant.Role.owner
        ).exists()

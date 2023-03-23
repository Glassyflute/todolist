from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from bot.models import TgUser
from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient


class BotVerificationView(GenericAPIView):
    """
    Позволяет подтвердить пользователя на основе кода верификации из сериализатора, отправляет сообщение в чате
    Телеграм об успешном подтверждении и связывании аккаунта пользователя Телеграм и пользователя из БД.
    """
    model = TgUser
    serializer_class = TgUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request: Request, *args, **kwargs):
        serializer_: TgUserSerializer = self.get_serializer(data=request.data)
        serializer_.is_valid(raise_exception=True)

        # пробрасываем пользователя в модель
        serializer_.tg_user.user = request.user
        serializer_.tg_user.save()
        tg_user_serialized = serializer_.tg_user

        TgClient().get_send_message(tg_user_serialized.tg_chat_id, "Verification was successful")
        return Response(self.get_serializer(tg_user_serialized).data)

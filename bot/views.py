from rest_framework.generics import UpdateAPIView

from bot.models import TgUser
from bot.serializers import TgUserSerializer


class BotVerificationView(UpdateAPIView):
    model = TgUser
    serializer_class = TgUserSerializer


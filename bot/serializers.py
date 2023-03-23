from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bot.models import TgUser
from core.models import User


class TgUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор выводит информацию по модели TgUser и сверяет код верификации, присвоенный пользователю в модели
    TgUser, с введенным пользователем кодом в приложении.
    """
    tg_id = serializers.SlugField(source="tg_chat_id", read_only=True)
    username = serializers.SlugField(source="tg_username", read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TgUser
        fields = ["tg_id", "username", "verification_code", "user"]
        read_only_fields = ("tg_id", "username", "user")

    def validate_verification_code(self, code: str) -> str:
        try:
            self.tg_user = TgUser.objects.get(verification_code=code)
        except TgUser.DoesNotExist:
            raise ValidationError("Incorrect verification code")
        return code

    def update(self, instance: TgUser, validated_data: dict):
        return super().update(instance, validated_data)

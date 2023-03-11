from rest_framework import serializers

from bot.models import TgUser


class TgUserSerializer(serializers.ModelSerializer):
    # tg_username = serializers.SlugRelatedField(slug_field="username", queryset=TgUser.objects.all())

    class Meta:
        model = TgUser
        fields = "__all__"

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bot.models import TgUser
from core.models import User


class TgUserSerializer(serializers.ModelSerializer):
    tg_id = serializers.SlugField(source="tg_chat_id", read_only=True)
    username = serializers.SlugField(source="tg_username", read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    # user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # user = serializers.PrimaryKeyRelatedField(source="username", queryset=User.objects.all(), read_only=True)
    # user = serializers.PrimaryKeyRelatedField(source="username", read_only=True)

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
        # instance.verification_code = validated_data.get("verification_code")
        # instance.username = validated_data.get("tg_username")
        # instance.user = validated_data.get("user")
        # instance.tg_id = validated_data.get("tg_chat_id")

    # def update(self, instance: TgUser, validated_data):
    #     # user_req_id = self.context["request"].user.id
    #     # verification_code = validated_data.get("verification_code")
    #     #
    #     # tg_user = TgUser.objects.filter(verification_code=verification_code).update(user=user_req_id)   # int?
    #     #
    #     # tg_user.save()
    #     # return tg_user
    #
    #     instance.user = self.context["request"].user.id
    #     instance.verification_code = validated_data.get("verification_code")
    #     # instance.save()
    #     instance.save(update_fields=["verification_code", "user"])
    #     return instance

        # with transaction.atomic():
        #     if verification_code := validated_data.get("verification_code"):
        #         tg_user = TgUser.objects.filter(verification_code=verification_code)
        #         tg_user.verification_code = verification_code
        #         tg_user.user = self.context["request"].user.id
        #         tg_user.save()
                # tg_user.save(update_fields=["verification_code"])

                # instance.verification_code = verification_code
                # instance.save(update_fields=["verification_code"])

        # self.tg_user.user = self.context["request"].user
        # self.tg_user.save()
        # AttributeError: 'QuerySet' object has no attribute 'save'

        # return super().update(instance, validated_data)
        # return tg_user

        # with transaction.atomic():
        #     if verification_code := validated_data.get("verification_code"):
        #         tg_user = TgUser.objects.filter(verification_code=verification_code)
        #         tg_user.verification_code = verification_code
        #         tg_user.save(update_fields=["verification_code"])
        #
        #         # instance.verification_code = verification_code
        #         # instance.save(update_fields=["verification_code"])
        #
        # return tg_user



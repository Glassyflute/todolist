from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from core.models import User


class PasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs["style"] = {"input_type": "password"}
        kwargs.setdefault("write_only", True)
        super().__init__(**kwargs)


class UserSignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор получает данные пользователя для регистрации, проверяет и шифрует пароль.
    """
    password = PasswordField(required=True)
    password_repeat = PasswordField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password", "password_repeat"]

    def validate(self, user_data: dict) -> dict:
        if user_data["password"] != user_data["password_repeat"]:
            raise serializers.ValidationError("Passwords must be identical to sign up.")
        return user_data

    def validate_password(self, password: str) -> str:
        user = self.context['request'].user
        validate_password(password, user=user)
        return password

    def create(self, validated_data: dict) -> User:
        del validated_data["password_repeat"]
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class LoginSerializer(serializers.ModelSerializer):
    """
    Сериализатор получает username, password от пользователя и проводит аутентификацию пользователя.
    """
    username = serializers.CharField(required=True)
    password = PasswordField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "first_name", "last_name", "email"]
        read_only_fields = ["id", "first_name", "last_name", "email"]

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        user = authenticate(validated_data, username=username, password=password)

        if not user:
            raise AuthenticationFailed
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор на отображение информации по профилю пользователя.
    """
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class PasswordUpdateSerializer(serializers.Serializer):
    """
    Сериализатор получает старый и новый пароли пользователя, сохраняет новый пароль.
    """
    old_password = PasswordField(required=True)
    new_password = PasswordField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "old_password", "new_password"]

    def validate_old_password(self, old_password):
        if not self.instance.check_password(old_password):
            raise serializers.ValidationError("Incorrect old password.")
        return old_password

    def validate(self, validated_data: dict) -> dict:
        if validated_data["old_password"] == validated_data["new_password"]:
            raise serializers.ValidationError("New password must differ from your old password.")
        return validated_data

    def validate_new_password(self, new_password: str) -> str:
        user = self.context['request'].user
        validate_password(new_password, user=user)
        return new_password

    def update(self, instance: User, validated_data: dict) -> User:
        instance.set_password(validated_data["new_password"])
        instance.save(update_fields=["password"])
        return instance

from django.contrib.auth import login, logout, update_session_auth_hash
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import User
from core.serializers import *


class UserSignUpView(CreateAPIView):
    """
    Создание (регистрация) нового пользователя
    """
    serializer_class = UserSignUpSerializer


class LoginView(CreateAPIView):
    """
    Страница входа по логину и паролю для зарегистрированного пользователя
    """
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login(request=request, user=serializer.save())
        return Response(serializer.data)


class UserProfileView(RetrieveUpdateDestroyAPIView):
    """
    Страница профиля пользователя
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        logout(self.request)


class PasswordUpdateView(UpdateAPIView):
    """
    Обновление пароля по пользователю
    """
    serializer_class = PasswordUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        update_session_auth_hash(self.request, user)

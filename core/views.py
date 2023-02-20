from django.contrib.auth import authenticate, login, logout
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from core.models import User
from core.serializers import *


class UserSignUpView(CreateAPIView):
    """
    Создание (регистрация) нового пользователя
    """
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer


class LoginView(CreateAPIView):
    """
    Страница входа по логину и паролю для зарегистрированного пользователя
    """
    queryset = User.objects.all()
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super().create(request, *args, **kwargs)


class UserProfileView(RetrieveUpdateDestroyAPIView):
    """
    Страница профиля пользователя
    """
    queryset = User.objects.all()
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
    queryset = User.objects.all()
    serializer_class = PasswordUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

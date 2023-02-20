from django.urls import path

from core.views import *

urlpatterns = [
    path("signup/", UserSignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("update_password/", PasswordUpdateView.as_view(), name="update_password"),
]

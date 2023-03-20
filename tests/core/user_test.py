from core.models import User

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserTest(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username="james_bond", email="james_bond@gmail.com",
                                                       password="bond_password")
        self.user = User.objects.create_user(username="Dianerys", email="dian@mail.ru", password="Dian_password")

    def test_user_create(self):
        url = reverse("signup")
        data = {"username": "test_username", "password": "test_password", "password_repeat": "test_password"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username=data["username"]).count(), 1)

    def test_user_login_success(self):
        url = reverse("signup")
        data = {"username": "test_username", "password": "test_password", "password_repeat": "test_password"}
        response = self.client.post(url, data, format='json')

        url = reverse("login")
        data = {"username": "test_username", "password": "test_password"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)     # 200 != 403
        self.assertEqual(User.objects.filter(username=data["username"]).count(), 1)

    def test_show_user_profile(self):
        self.client.force_login(self.user)

        url = reverse("profile")
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_obj = User.objects.get(username=self.user.username)
        self.assertEqual(user_obj.username, "Dianerys")
        self.assertNotEqual(user_obj.username, self.superuser.username)

    def test_update_user_profile(self):
        self.client.force_login(self.user)

        url = reverse("profile")
        data = {"username": "Dianerys", "first_name": "Diana", "last_name": "Smith", "email": "dia@mail.ru"}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.filter(username=self.user.username).count(), 1)

        user_obj = User.objects.get(username=self.user.username)
        self.assertEqual(user_obj.first_name, data["first_name"])
        self.assertEqual(user_obj.last_name, data["last_name"])
        self.assertEqual(user_obj.email, data["email"])
        self.assertNotEqual(user_obj.username, "test_username")

    def test_partial_update_user_profile(self):
        self.client.force_login(self.user)

        url = reverse("profile")
        data = {"first_name": "Dia", "email": "dia_different@mail.ru"}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.filter(username=self.user.username).count(), 1)

        user_obj = User.objects.get(username=self.user.username)
        self.assertEqual(user_obj.first_name, data["first_name"])
        self.assertEqual(user_obj.email, data["email"])
        self.assertEqual(user_obj.username, "Dianerys")
        self.assertEqual(user_obj.last_name, "")
        self.assertNotEqual(user_obj.username, "test_username")

    def test_delete_user(self):
        self.client.force_login(self.user)

        url = reverse("profile")
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.filter(username=self.user.username).count(), 1)

    def test_change_password(self):
        self.client.force_login(self.user)

        url = reverse("update_password")
        data = {"old_password": "Dian_password", "new_password": "updated_password_new"}
        response = self.client.put(url, data, format='json')

        # self.user.set_password(data["new_password"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.filter(username=self.user.username).count(), 1)

        # user_obj = User.objects.get(username=self.user.username)
        # self.assertEqual(user_obj.password, self.user.password)

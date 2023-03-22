from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import User
from goals.models import GoalCategory, Board


class HelpfulTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Dianerys", email="dian@mail.ru", password="Dian_password")
        self.client.force_login(self.user)

    def create_board(self):
        url = reverse("board-create")
        data = {"title": "test_board"}
        response = self.client.post(url, data, format='json')
        return response

    def create_category_in_db(self):
        response_board = self.create_board()
        board_dict = response_board.data
        board = Board.objects.get(pk=board_dict["id"])

        category_obj = GoalCategory.objects.create(title="category_title", board=board, user=self.user)
        return category_obj


class GoalCategoryTest(HelpfulTest):
    def test_category_get_list(self):
        response_board = self.create_board()
        board_dict = response_board.data
        board = Board.objects.get(pk=board_dict["id"])

        category_one = GoalCategory.objects.create(title="category_one", board=board, user=self.user)
        category_two = GoalCategory.objects.create(title="category_two", board=board, user=self.user)

        url = reverse("category-list")
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(GoalCategory.objects.count(), 2)
        self.assertIn(category_one, GoalCategory.objects.all())
        self.assertIn(category_two, GoalCategory.objects.all())

    def test_category_get_detail(self):
        response_board = self.create_board()

        url_cat = reverse("category-create")
        data_cat = {"title": "new_category_title", "board": response_board.data["id"]}
        response_cat = self.client.post(url_cat, data_cat, format='json')
        self.assertEqual(response_cat.status_code, status.HTTP_201_CREATED)

        url_detailed = reverse("category-detail", kwargs={"pk": response_cat.data["id"]})
        res = self.client.get(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(GoalCategory.objects.filter(pk=response_cat.data["id"]).count(), 1)

        category_obj = GoalCategory.objects.get(pk=response_cat.data["id"])
        self.assertEqual(category_obj.title, res.data["title"])

    def test_category_get_detail_for_db_category(self):
        category = self.create_category_in_db()

        url_detailed = reverse("category-detail", kwargs={"pk": category.pk})
        res = self.client.get(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(GoalCategory.objects.filter(pk=category.pk).count(), 1)

    def test_category_update(self):
        response_board = self.create_board()

        url_cat = reverse("category-create")
        data_cat = {"title": "new_category_title", "board": response_board.data["id"]}
        response_cat = self.client.post(url_cat, data_cat, format='json')
        self.assertEqual(response_cat.status_code, status.HTTP_201_CREATED)

        url_detailed = reverse("category-detail", kwargs={"pk": response_cat.data["id"]})
        data = {"title": "category_updated_title"}
        res = self.client.patch(url_detailed, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(GoalCategory.objects.filter(pk=response_cat.data["id"]).count(), 1)

        category_obj = GoalCategory.objects.get(pk=response_cat.data["id"])
        self.assertEqual(category_obj.title, res.data["title"])

    def test_category_update_for_db_category(self):
        category = self.create_category_in_db()

        url_detailed = reverse("category-detail", kwargs={"pk": category.pk})
        data = {"title": "category_updated_title"}
        res = self.client.patch(url_detailed, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(GoalCategory.objects.filter(pk=category.pk).count(), 1)

        category_obj = GoalCategory.objects.get(pk=category.pk)
        self.assertEqual(category_obj.title, res.data["title"])

    def test_category_delete(self):
        response_board = self.create_board()

        url_cat = reverse("category-create")
        data_cat = {"title": "new_category_title", "board": response_board.data["id"]}
        response_cat = self.client.post(url_cat, data_cat, format='json')
        self.assertEqual(response_cat.status_code, status.HTTP_201_CREATED)

        url_detailed = reverse("category-detail", kwargs={"pk": response_cat.data["id"]})
        res = self.client.delete(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(GoalCategory.objects.filter(pk=response_cat.data["id"]).count(), 1)

    def test_category_delete_for_db_category(self):
        category = self.create_category_in_db()

        url_detailed = reverse("category-detail", kwargs={"pk": category.pk})
        res = self.client.delete(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(GoalCategory.objects.filter(pk=category.pk).count(), 1)

    def test_category_create(self):
        response_board = self.create_board()

        url = reverse("category-create")
        data = {"title": "new_category_title", "board": response_board.data["id"]}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GoalCategory.objects.filter(title=data["title"]).count(), 1)

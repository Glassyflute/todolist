from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import User
from goals.models import Board, GoalCategory, Goal


class HelpfulTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Dianerys", email="dian@mail.ru", password="Dian_password")
        self.client.force_login(self.user)
        self.board = Board.objects.create(title="Board_Gamma")
        self.category = GoalCategory.objects.create(title="category_Gamma", board=self.board, user=self.user)
        self.goal = Goal.objects.create(title="goal_Zero", category=self.category, user=self.user)

    def create_board(self):
        url = reverse("board-create")
        data = {"title": "test_board"}
        response = self.client.post(url, data, format='json')
        return response

    def create_category(self):
        response_board = self.create_board()

        url_cat = reverse("category-create")
        data_cat = {"title": "new_category_title", "board": response_board.data["id"]}
        response_cat = self.client.post(url_cat, data_cat, format='json')
        return response_cat


class GoalTest(HelpfulTest):
    def test_goal_create(self):
        response_cat = self.create_category()

        url = reverse("goal-create")
        data = {"title": "test_goal", "category": response_cat.data["id"]}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Goal.objects.filter(title=data["title"]).count(), 1)
        self.assertEqual(Goal.objects.filter(pk=response.data["id"]).count(), 1)

    def test_goal_get_list(self):
        goal_beta = Goal.objects.create(title="Goal_Beta", category=self.category, user=self.user)
        goal_alpha = Goal.objects.create(title="Goal_Alpha", category=self.category, user=self.user)

        url = reverse("goal-list")
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Goal.objects.count(), 3)
        self.assertIn(goal_alpha, Goal.objects.all())
        self.assertIn(goal_beta, Goal.objects.all())

    def test_goal_get_detail(self):
        response_cat = self.create_category()

        url = reverse("goal-create")
        data = {"title": "test_goal", "category": response_cat.data["id"]}
        response_goal = self.client.post(url, data, format='json')
        self.assertEqual(response_goal.status_code, status.HTTP_201_CREATED)

        url_detailed = reverse("goal-detail", kwargs={"pk": response_goal.data["id"]})
        res = self.client.get(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Goal.objects.filter(pk=response_goal.data["id"]).count(), 1)

        goal_obj = Goal.objects.get(pk=response_goal.data["id"])
        self.assertEqual(goal_obj.title, res.data["title"])

    def test_goal_update(self):
        response_cat = self.create_category()

        url = reverse("goal-create")
        data = {"title": "test_goal", "category": response_cat.data["id"]}
        response_goal = self.client.post(url, data, format='json')
        self.assertEqual(response_goal.status_code, status.HTTP_201_CREATED)

        url_detailed = reverse("goal-detail", kwargs={"pk": response_goal.data["id"]})
        data = {"title": "goal_updated_title"}
        res = self.client.patch(url_detailed, data, format='json')
        # res = self.client.put(url_detailed, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Goal.objects.filter(pk=response_goal.data["id"]).count(), 1)

        goal_obj = Goal.objects.get(pk=response_goal.data["id"])
        self.assertEqual(goal_obj.title, res.data["title"])

    def test_goal_partial_update(self):
        response_cat = self.create_category()

        url = reverse("goal-create")
        data = {"title": "test_goal", "category": response_cat.data["id"]}
        response_goal = self.client.post(url, data, format='json')
        self.assertEqual(response_goal.status_code, status.HTTP_201_CREATED)

        response_cat_two = self.create_category()

        url_detailed = reverse("goal-detail", kwargs={"pk": response_goal.data["id"]})
        data = {"title": "goal_updated_title", "category": response_cat_two.data["id"]}
        res = self.client.put(url_detailed, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Goal.objects.filter(pk=response_goal.data["id"]).count(), 1)

        goal_obj = Goal.objects.get(pk=response_goal.data["id"])
        self.assertEqual(goal_obj.title, res.data["title"])
        self.assertEqual(goal_obj.category.pk, res.data["category"])

    def test_goal_delete(self):
        response_cat = self.create_category()

        url = reverse("goal-create")
        data = {"title": "test_goal", "category": response_cat.data["id"]}
        response_goal = self.client.post(url, data, format='json')
        self.assertEqual(response_goal.status_code, status.HTTP_201_CREATED)

        url_detailed = reverse("goal-detail", kwargs={"pk": response_goal.data["id"]})
        res = self.client.delete(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Goal.objects.filter(pk=response_goal.data["id"]).count(), 1)

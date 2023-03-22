from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import User
from goals.models import Board, GoalComment, Goal, GoalCategory


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

    def create_goal(self):
        response_cat = self.create_category()

        url = reverse("goal-create")
        data = {"title": "test_goal", "category": response_cat.data["id"]}
        response_goal = self.client.post(url, data, format='json')
        return response_goal


class CommentTest(HelpfulTest):
    def test_comment_create(self):
        response_goal = self.create_goal()

        url = reverse("comment-create")
        data = {"text": "test_comment_text", "goal": response_goal.data["id"]}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GoalComment.objects.filter(pk=response.data["id"]).count(), 1)

    def test_comment_get_list(self):
        comment_one = GoalComment.objects.create(text="comment_one", goal=self.goal, user=self.user)
        comment_two = GoalComment.objects.create(text="comment_two", goal=self.goal, user=self.user)

        url = reverse("comment-list")
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(GoalComment.objects.count(), 2)
        self.assertIn(comment_two, GoalComment.objects.all())

    def test_comment_get_detail(self):
        response_goal = self.create_goal()

        url = reverse("comment-create")
        data = {"text": "test_comment_text", "goal": response_goal.data["id"]}
        response_comment = self.client.post(url, data, format='json')
        self.assertEqual(response_comment.status_code, status.HTTP_201_CREATED)

        url_detailed = reverse("comment-detail", kwargs={"pk": response_comment.data["id"]})
        res = self.client.get(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(GoalComment.objects.filter(pk=response_comment.data["id"]).count(), 1)

        comment_obj = GoalComment.objects.get(pk=response_comment.data["id"])
        self.assertEqual(comment_obj.text, res.data["text"])

    def test_comment_update(self):
        response_goal = self.create_goal()

        url = reverse("comment-create")
        data = {"text": "test_comment_text", "goal": response_goal.data["id"]}
        response_comment = self.client.post(url, data, format='json')
        self.assertEqual(response_comment.status_code, status.HTTP_201_CREATED)

        url_detailed = reverse("comment-detail", kwargs={"pk": response_comment.data["id"]})
        data = {"text": "updated_comment_text"}
        res = self.client.patch(url_detailed, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(GoalComment.objects.filter(pk=response_comment.data["id"]).count(), 1)

        comment_obj = GoalComment.objects.get(pk=response_comment.data["id"])
        self.assertEqual(comment_obj.text, res.data["text"])

    def test_comment_delete(self):
        response_goal = self.create_goal()

        url = reverse("comment-create")
        data = {"text": "test_comment_text", "goal": response_goal.data["id"]}
        response_comment = self.client.post(url, data, format='json')
        self.assertEqual(response_comment.status_code, status.HTTP_201_CREATED)

        url_detailed = reverse("comment-detail", kwargs={"pk": response_comment.data["id"]})
        res = self.client.delete(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(GoalComment.objects.filter(pk=response_comment.data["id"]).count(), 0)

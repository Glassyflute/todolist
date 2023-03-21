import json

from django.core import serializers
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import User
from core.serializers import UserProfileSerializer
from goals.models import GoalCategory, Board, BoardParticipant
from goals.serializers import BoardSerializer


class HelpfulTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Dianerys", email="dian@mail.ru", password="Dian_password")
        self.client.force_login(self.user)
        # self.board = self.create_board_instance_with_boardparticipant()

    # def create_board_instance_with_boardparticipant(self):
    def create_board(self):
        url = reverse("board-create")
        data = {"title": "test_board"}
        response = self.client.post(url, data, format='json')
        return response

        # board_dict = response.data
        # board = Board.objects.get(pk=board_dict["id"])
        # BoardParticipant.objects.create(user=self.user, board=board, role=1)
        # return response
        # django.db.utils.IntegrityError: duplicate key value violates unique constraint "goals_boardparticipant_board_id_user_id_95ba82a9_uniq"
        # E               DETAIL:  Key (board_id, user_id)=(1, 1) already exists.

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

        category_obj = GoalCategory.objects.create(title="category_title", board=board, user=self.user)

        url = reverse("category-list")
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(GoalCategory.objects.count(), 1)
        self.assertIn(category_obj, GoalCategory.objects.all())

    def test_category_get_detail(self):
        response_board = self.create_board()
        board_dict = response_board.data
        board = Board.objects.get(pk=board_dict["id"])

        url = reverse("category-create")
        # create category problems if data["user"] делаем не строкой, а пробуем self.user
        data = {"title": "new_category_title", "board": board_dict, "user": "user_test"}
        response = self.client.post(url, data, format='json')

        url_detailed = reverse("category-detail", kwargs={"pk": response.data["id"]})
        res = self.client.get(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # self.assertEqual(GoalCategory.objects.filter(title=data["title"]).count(), 1)
        self.assertEqual(GoalCategory.objects.filter(pk=data["pk"]).count(), 1)

        category_obj = GoalCategory.objects.get(pk=response.data["id"])
        self.assertEqual(category_obj.title, res.data["title"])

    def test_category_get_detail_for_db_category(self):
        category = self.create_category_in_db()

        url_detailed = reverse("category-detail", kwargs={"pk": category.pk})
        res = self.client.get(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(GoalCategory.objects.filter(pk=category.pk).count(), 1)

    def test_category_update(self):
        response_board = self.create_board()
        board_dict = response_board.data
        board = Board.objects.get(pk=board_dict["id"])

        url = reverse("category-create")
        # create category problems if data["user"] делаем не строкой, а пробуем self.user
        data = {"title": "new_category_title", "board": board_dict, "user": "user_test"}
        response = self.client.post(url, data, format='json')

        url_detailed = reverse("category-detail", kwargs={"pk": response.data["id"]})
        data = {"title": "category_updated_title"}
        res = self.client.patch(url_detailed, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(GoalCategory.objects.filter(pk=data["pk"]).count(), 1)

        category_obj = GoalCategory.objects.get(pk=response.data["id"])
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
        board_dict = response_board.data
        board = Board.objects.get(pk=board_dict["id"])

        url = reverse("category-create")
        # create category problems if data["user"] делаем не строкой, а пробуем self.user
        data = {"title": "new_category_title", "board": board_dict, "user": "user_test"}
        response = self.client.post(url, data, format='json')

        url_detailed = reverse("category-detail", kwargs={"pk": response.data["id"]})
        res = self.client.delete(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(GoalCategory.objects.filter(pk=response.data["id"]).count(), 1)

    def test_category_delete_for_db_category(self):
        category = self.create_category_in_db()

        url_detailed = reverse("category-detail", kwargs={"pk": category.pk})
        res = self.client.delete(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(GoalCategory.objects.filter(pk=category.pk).count(), 1)





    def test_category_create_str_for_board_user(self):
        url = reverse("category-create")
        # data = {"title": "new_category_title", "board": "board_test", "user": "user_test",
        #         "created": "2023-03-20T16:48:41.085767Z", "updated": "2023-03-20T16:48:41.085767Z",
        #         "is_deleted": False
        #         }
        data = {"title": "new_category_title", "board": "board_test", "user": "user_test"}

        response = self.client.post(url, data, format='json')
        # 404 Not Found: /goal_categorycreate
        # response = self.client.post(url, data=json.dumps(data), content_type="application/json")

        self.assertContains(response, 200)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(GoalCategory.objects.filter(title=data["title"]).count(), 1)

    def test_category_create(self):
        response_board = self.create_board()
        board_dict = response_board.data
        board = Board.objects.get(pk=board_dict["id"])

        url = reverse("category-create")
        # create category problems if data["user"] делаем не строкой, а пробуем self.user
        # здесь в тесте имеем Bad Request: /goals/goal_category/create -- 201 != 400
        data = {"title": "new_category_title", "board": board_dict, "user": "user_test"}
        response = self.client.post(url, data, format='json')

        # response_board = self.create_board()
        # board_dict = response_board.data
        # board = Board.objects.get(pk=board_dict["id"])
        #
        # url = reverse("category-create")
        # # create category problems if data["user"] делаем не строкой, а пробуем self.user
        # data = {"title": "new_category_title", "board": board_dict, "user": "user_test"}
        # response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GoalCategory.objects.filter(title=data["title"]).count(), 1)



        # user = UserProfileSerializer(self.user).data
        # data = {"title": "new_category_title", "board": board_dict, "user": user}
        # 400 error: Bad Request: /goals/goal_category/create

        # user_qs = User.objects.filter(pk=self.user.pk)
        # serializer = UserProfileSerializer(user_qs)
        # data = {"title": "new_category_title", "board": board_dict, "user": serializer.data}
        # AttributeError: 'QuerySet' object has no attribute 'username'
        # AttributeError: Got AttributeError when attempting to get a value for field `username` on serializer `UserProfileSerializer`.
        # The serializer field might be named incorrectly and not match any attribute or key on the `QuerySet` instance.

        # user_qs_to_json = serializers.serialize("json", user_qs)
        # data = {"title": "new_category_title", "board": board_dict, "user": user_qs_to_json}    # 400 error
        # data = {"title": "new_category_title", "board": board_dict, "user": UserProfileSerializer(self.user).data["user"]}
        # KeyError: 'user'

        # response = self.client.post(url, data, format='json')
        # # res = response.json()
        #
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(GoalCategory.objects.filter(title=data["title"]).count(), 1)



    # url = reverse("category-create")
    # data = {"title": "category_two", "board": board, "user": self.user}
    # res = self.client.post(url, data, format='json')
    # return res


    # def test_category_get_list(self):
    #     response = self.create_category()
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     url = reverse("category-list")
    #     res = self.client.get(url, format='json')
    #
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(GoalCategory.objects.count(), 1)





    # def setUp(self):
    #     self.user = User.objects.create_user(username="Dianerys", email="dian@mail.ru", password="Dian_password")
    #     self.client.force_login(self.user)
    #     self.board = Board.objects.create(title="Board_one")
    #     # self.date = "2023-03-20T16:48:41.085767Z"
    #     self.category = GoalCategory.objects.create(title="category_one", board=self.board, user=self.user)
    #     # self.boardparticipant = BoardParticipant.objects.create(user=self.user, board=self.board, role=1)

    # problems 400 error
    # def test_board_create(self):
    #     url = reverse("category-create")
    #     data = {"title": "test_category",
    #             "board": BoardSerializer(self.board).data,  # 'ReturnDict' object
    #             "user": UserProfileSerializer(self.user).data
    #             }
    #     # data = {"title": "test_category",
    #     #         "board": self.board,    # TypeError: Object of type Board is not JSON serializable
    #     #         "user": self.user
    #     #         }
    #     response = self.client.post(url, data, format='json')
    #
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)     # Bad Request: 400
    #     self.assertEqual(GoalCategory.objects.filter(title=data["title"]).count(), 1)


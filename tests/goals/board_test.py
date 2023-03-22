from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import User
from goals.models import Board, BoardParticipant


class BoardTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Dianerys", email="dian@mail.ru", password="Dian_password")
        self.client.force_login(self.user)

    def test_board_create(self):
        url = reverse("board-create")
        data = {"title": "test_board"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Board.objects.filter(title=data["title"]).count(), 1)

    def test_boardparticipant_create_with_board(self):
        board_two = Board.objects.create(title="Board_two")
        board_participant = BoardParticipant.objects.create(user=self.user, board=board_two, role=1)
        self.assertEqual(Board.objects.filter(pk=board_two.pk).count(), 1)
        self.assertEqual(BoardParticipant.objects.filter(pk=board_participant.pk).count(), 1)

        url = reverse("boardparticipant-list")
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(board_participant, BoardParticipant.objects.all())

    def test_board_get_list(self):
        board_one = Board.objects.create(title="Board_one")
        board_two = Board.objects.create(title="Board_two")

        url = reverse("board-list")
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Board.objects.count(), 2)
        self.assertIn(board_two, Board.objects.all())

    def test_board_get_detail(self):
        url = reverse("board-create")
        data = {"title": "board_new_title"}
        response = self.client.post(url, data, format='json')

        url_detailed = reverse("board-detail", kwargs={"pk": response.data["id"]})
        res = self.client.get(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Board.objects.filter(title=data["title"]).count(), 1)

        board_obj = Board.objects.get(pk=response.data["id"])
        self.assertEqual(board_obj.title, res.data["title"])

    def test_board_update(self):
        url = reverse("board-create")
        data = {"title": "board_new_title"}
        response = self.client.post(url, data, format='json')

        url_detailed = reverse("board-detail", kwargs={"pk": response.data["id"]})
        data = {"title": "board_updated_title"}
        res = self.client.patch(url_detailed, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Board.objects.filter(title=data["title"]).count(), 1)

        board_obj = Board.objects.get(pk=response.data["id"])
        self.assertEqual(board_obj.title, res.data["title"])

    def test_board_delete(self):
        url = reverse("board-create")
        data = {"title": "board_new_title"}
        response = self.client.post(url, data, format='json')

        url_detailed = reverse("board-detail", kwargs={"pk": response.data["id"]})
        res = self.client.delete(url_detailed, format='json')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Board.objects.filter(title=data["title"]).count(), 1)

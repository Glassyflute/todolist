from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant
from goals.permissions import BoardPermissions, GoalCategoryPermissions, GoalPermissions, GoalCommentPermissions

from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, \
    GoalCommentCreateSerializer, GoalSerializer, GoalCommentSerializer, BoardSerializer, BoardCreateSerializer, \
    BoardParticipantSerializer, BoardListSerializer


# GoalCategory
class GoalCategoryCreateView(CreateAPIView):
    """
    Позволяет создать категорию пользователю с разрешениями IsAuthenticated, GoalCategoryPermissions.
    """
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    """
    Позволяет пользователю с разрешениями IsAuthenticated, GoalCategoryPermissions видеть информацию по
    актуальным категориям, в досках которых он является участником, а также созданные им категории.
    Встроены сортировка, фильтрация по названию актуальной категории.
    """
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["board", "user"]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        return GoalCategory.objects.filter(board__participants__user=self.request.user, is_deleted=False)


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """
    Позволяет пользователю с разрешениями IsAuthenticated, GoalCategoryPermissions видеть информацию по
    актуальным категориям, в досках которых он является участником, а также созданные им категории. Пользователь
    может обновлять или удалять категорию в зависимости от прописанных ролей доступа и участия в доске.
    При удалении категории все цели этой категории переходят в статус «Архив» и не показываются в списке актуальных
    целей, однако остаются в БД.
    """
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]

    def get_queryset(self):
        return GoalCategory.objects.filter(board__participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.goals.update(status=Goal.Status.archived)
        return instance


# Goal
class GoalCreateView(CreateAPIView):
    """
    Позволяет пользователю с разрешениями IsAuthenticated, GoalPermissions создать цель.
    """
    model = Goal
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    """
    Позволяет пользователю с разрешениями IsAuthenticated, GoalPermissions видеть список актуальных целей, в досках
    которых он является участником, а также созданные им цели.
    Встроены сортировка по приоритету и дедлайну, а также фильтрация по названию и описанию цели. При удалении категории
    все цели этой категории переходят в статус «Архив» и не показываются в списке актуальных целей, однако остаются
    в БД.
    """
    model = Goal
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ["priority", "due_date"]
    ordering = ["due_date", "priority"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        # пользователь видит созданные пользователем актуальные цели, а также цели с актуальными категориями,
        # в досках которых он является участником
        return Goal.objects.filter(category__board__participants__user=self.request.user,
                                   category__is_deleted=False).exclude(status=Goal.Status.archived)


class GoalView(RetrieveUpdateDestroyAPIView):
    """
    Позволяет пользователю с разрешениями IsAuthenticated, GoalPermissions видеть информацию по созданным пользователем
    актуальным цели, а также целям с актуальными категориями, в досках которых он является участником. Пользователь
    может обновлять или удалять цель в зависимости от прописанных ролей доступа и участия в доске.
    Цель не показывается, если присвоенная ей категория имеет статус удалена/архивирована, однако подобные цели и
    категории остаются в БД.
    """
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]

    def get_queryset(self):
        return Goal.objects.filter(category__board__participants__user=self.request.user,
                                   category__is_deleted=False).exclude(status=Goal.Status.archived)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.status = Goal.Status.archived
            instance.save()
            return instance


# GoalComment
class GoalCommentCreateView(CreateAPIView):
    """
    Позволяет пользователю с разрешениями IsAuthenticated, GoalCommentPermissions создать комментарий к цели.
    """
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated, GoalCommentPermissions]
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(ListAPIView):
    """
    Позволяет пользователю с разрешениями IsAuthenticated, GoalCommentPermissions видеть список своих комментариев и
    комментарии к актуальным целям и категориям, в досках которых он является участником.
    Встроены сортировка, фильтрация по тексту комментария и цели. Комментарии удаляются полностью при удалении
    Пользователя или Цели, не сохраняются в БД.
    """
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated, GoalCommentPermissions]
    serializer_class = GoalCommentSerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['goal']
    ordering_fields = ["created"]
    ordering = ["text"]
    search_fields = ["text"]

    def get_queryset(self):
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    """
    Позволяет пользователю с разрешениями IsAuthenticated, GoalCommentPermissions видеть информацию по созданным
    пользователем неудаленным комментариям к актуальным целям и категориям, в досках которых он является участником.
    Пользователь может обновлять или удалять комментарий в зависимости от прописанных ролей доступа и участия в доске.
    Комментарии удаляются полностью при удалении Пользователя или Цели, не сохраняются в БД.
    """
    model = GoalComment
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated, GoalCommentPermissions]

    def get_queryset(self):
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


# Board
class BoardCreateView(CreateAPIView):
    """
    Позволяет пользователю со статусом IsAuthenticated создать доску и получить в ней роль "владелец".
    """
    model = Board
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardCreateSerializer

    def perform_create(self, serializer):
        BoardParticipant.objects.create(user=self.request.user, board=serializer.save(),
                                        role=BoardParticipant.Role.owner)


class BoardListView(ListAPIView):
    """
    Позволяет пользователю с разрешениями IsAuthenticated, BoardPermissions видеть список своих досок и досок, в которых
    он является участником. Фильтрация по актуальным доскам идет через participants.
    Встроены сортировка, поиск по названию доски.
    """
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardListSerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["title"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)


class BoardView(RetrieveUpdateDestroyAPIView):
    """
    Позволяет пользователю с разрешениями IsAuthenticated, BoardPermissions видеть информацию по созданным пользователем
    актуальным доскам и доскам, в которых пользователь является участником. Фильтрация по актуальным доскам идет
    через participants. Пользователь с ролью "владелец" может обновлять или удалять доску.
    При удалении доски помечаем ее статус как is_deleted, присвоенные доске категории получают статус
    удалена/архивирована, цели получают статус архивирована, но не удаляются из БД.
    """
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        #
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: Board):
        #
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
        return instance


# для проверки в текущей домашке
class BoardParticipantListView(ListAPIView):
    model = BoardParticipant
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardParticipantSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return BoardParticipant.objects.filter(user=self.request.user)

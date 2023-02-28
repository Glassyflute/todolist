from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters

from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment

from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, \
    GoalCommentCreateSerializer, GoalSerializer, GoalCommentSerializer


class GoalCategoryCreateView(CreateAPIView):
    """
    Позволяет создать категорию пользователю со статусом IsAuthenticated.
    """
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    """
    Позволяет видеть список категорий пользователю со статусом IsAuthenticated. Встроены сортировка, фильтрация по
    названию актуальной категории.
    """
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """
    Позволяет пользователю со статусом IsAuthenticated видеть детальную информацию по актуальной категории, обновлять
    или удалять категорию. При удалении категории все цели этой категории переходят в статус «Архив» и не показываются
    в списке актуальных целей, однако остаются в БД.
    """
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.goals.update(status=Goal.Status.archived)
            return instance


class GoalCreateView(CreateAPIView):
    """
    Позволяет пользователю со статусом IsAuthenticated создать цель.
    """
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    """
    Позволяет пользователю со статусом IsAuthenticated видеть список актуальных целей. Встроены сортировка по приоритету
    и дедлайну, а также фильтрация по названию и описанию цели. При удалении категории все цели этой категории переходят
    в статус «Архив» и не показываются в списке актуальных целей, однако остаются в БД.
    """
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ["priority", "due_date"]
    ordering = ["due_date", "priority"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        return Goal.objects.filter(user_id=self.request.user.pk,
                                   category__is_deleted=False).exclude(status=Goal.Status.archived)


class GoalView(RetrieveUpdateDestroyAPIView):
    """
    Позволяет пользователю со статусом IsAuthenticated видеть детальную информацию по актуальной цели, обновлять
    или удалять цель. Цель не показывается, если присвоенная ей категория имеет статус удалена/архивирована, однако
    подобные цели и категории остаются в БД.
    """
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user_id=self.request.user.pk,
                                   category__is_deleted=False
                                   ).exclude(status=Goal.Status.archived)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.status = Goal.Status.archived
            instance.save()
            return instance


class GoalCommentCreateView(CreateAPIView):
    """
    Позволяет пользователю со статусом IsAuthenticated создать комментарий к цели.
    """
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(ListAPIView):
    """
    Позволяет пользователю со статусом IsAuthenticated видеть список комментариев. Встроены сортировка, фильтрация по
    тексту комментария и цели. Комментарии удаляются полностью при удалении Пользователя или Цели, не сохраняются в БД.
    """
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['goal']
    ordering_fields = ["created"]
    ordering = ["text"]
    search_fields = ["text"]

    def get_queryset(self):
        return GoalComment.objects.filter(user_id=self.request.user.pk)


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    """
    Позволяет пользователю со статусом IsAuthenticated видеть детальную информацию по существующему комментарию,
    обновлять или удалять комментарий. Комментарии удаляются полностью при удалении Пользователя или Цели, не
    сохраняются в БД.
    """
    model = GoalComment
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalComment.objects.filter(user_id=self.request.user.pk)

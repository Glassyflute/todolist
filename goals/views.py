from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters
###### from django_filters import rest_framework as filters

from rest_framework.pagination import LimitOffsetPagination

# from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment, Status
# how to refer to Status class inside Goal class?

from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, \
    GoalCommentCreateSerializer, GoalSerializer, GoalCommentSerializer


# category POST
class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


# # category GET list
class GoalCategoryListView(ListAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)


# category detail view by PK: GET, PUT/PATCH, DELETE
class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)

    # category DELETE by PK
    def perform_destroy(self, instance):
        instance.is_deleted = True
        # При удалении категории все цели этой категории переходят в статус «Архив»
        # ????

        instance.save()
        return instance


#############################
# added POST for goal
class GoalCreateView(CreateAPIView):
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCreateSerializer


# added GET list for goal
class GoalListView(ListAPIView):
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination

    # filter_backends = [
    #     DjangoFilterBackend,
    #     filters.OrderingFilter,
    #     filters.SearchFilter,
    #     # ...
    # ]
    # filterset_class = GoalDateFilter
    #
    # ordering_fields = ["-priority", "deadline"]
    # ordering = ["deadline", "-priority"]
    # search_fields = ["title", "description", "category", "priority"]

# Фильтрация должна быть  - по категории/категориям,  - приоритету/приоритетам,
# - дате дедлайна (от/до). ==
# Поиск должен быть не только по названию, но и по описанию
# Карточки по умолчанию в каждой колонке сортируются по приоритету (в порядке важности) и дате дедлайна
    # Должна быть возможность отсортировать карточки по дате дедлайна без учета приоритета

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user, is_deleted=False)


# goal detail view by PK: GET, PUT/PATCH, DELETE
class GoalView(RetrieveUpdateDestroyAPIView):
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user, is_deleted=False)

    # При редактировании цели должна меняться дата обновления. == ?????
    def perform_update(self, serializer):
        serializer.save()

    # goal DELETE by PK
    def perform_destroy(self, instance):
        instance.is_deleted = True
        # перемещение цели в архив при удалении
        instance.status = Status.archived
        instance.save()
        return instance


###############################################
# added POST for Comment
class GoalCommentCreateView(CreateAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentCreateSerializer


# #  GET list for Comments
class GoalCommentListView(ListAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["created"]  # по нарастанию
    ordering = ["text"]
    search_fields = ["text"]   # фильтрацию сделать по цели, к которой есть коммент

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user)
# убрать Юзера, взять Цель
        # goal=self.request.user.goal or self.request.goal-- обновить модель Юзера с FK по целям (и комментам? или не надо, из Цели все пойдет)


#  detail view for Comment by PK: GET, PUT/PATCH, DELETE
class GoalCommentView(RetrieveUpdateDestroyAPIView):
    model = GoalComment
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user)
        # self.request.user.goal -- обновить модель Юзера с FK по целям и комментам

    # Комментарии нужны, чтобы добавлять к цели примечания, ссылки, файлы, фото и что угодно по теме = здесь
    # на update или при создании ?

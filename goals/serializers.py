from datetime import *
from django.utils import timezone
from rest_framework import serializers

from core.serializers import UserProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"


class GoalCategorySerializer(serializers.ModelSerializer):
    # Убрана логика с подстановкой текущего пользователя в поле user.
    # Информация по пользователю выводится из сериализатора по пользователю.
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    # проверяем, что пользователь может создать комментарий только к своим актуальным целям
    def validate_goal(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("User is prohibited to comment on deleted goals.")

        if value.user != self.context["request"].user:
            raise serializers.ValidationError("User is not owner of this goal.")

        return value


class GoalCommentSerializer(serializers.ModelSerializer):
    # убрали логику с подстановкой текущего пользователя в поле user.
    user = UserProfileSerializer(read_only=True)
    goal = serializers.SerializerMethodField()

    def get_goal(self, goalcomment):
        return goalcomment.goal.title

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")
    # comments_for_goal


class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    comments = serializers.SerializerMethodField()

    def get_comments(self, goal):
        return [item.text for item in goal.goal_comment.all()]
    # comments = serializers.CharField() with error

    # user = UserProfileSerializer(read_only=True)
    # comments = serializers.SlugRelatedField(
    #     required=False,
    #     many=True,
    #     # queryset=GoalComment.objects.filter(user__username=user.context["request"].user.username),
    #     queryset=GoalComment.objects.all(),
    #     slug_field="text"
    # )

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"
        # exclude = ["comments"]

    # def is_valid(self, raise_exception=False):
    #     self._comments = self.initial_data.pop("comments", [])
    #     return super().is_valid(raise_exception=raise_exception)

    # Проверяем, что пользователь может назначить категорию только из своих актуальных категорий.
    # Если категория остается пустой при создании, то ей назначается Категория=Default по умолчанию.
    def validate_category(self, value):
        if value is not None:
            if value.is_deleted:
                raise serializers.ValidationError("User is prohibited to assign deleted categories for goals.")

            # проверяем, что категория создаваемой цели принадлежит пользователю,
            # т.е. пользователь не может создать цель в чужой категории
            if value.user != self.context["request"].user:
                raise serializers.ValidationError("User is not owner of this category.")
        else:
            value = GoalCategory.objects.create(title="Default", user=self.context["request"].user)

        return value

    def validate_due_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value


class GoalSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    # comments = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field="text"
    # )
    # comments = serializers.CharField()  # goals.GoalComment.None

    comments = serializers.SerializerMethodField()
    def get_comments(self, goal):
        return [item.text for item in goal.goal_comment.all()]

    ## отображать список комментов на карточке Цели
    # queryset=GoalComment.objects.filter(user_id=self.context["request"].user.pk)
    # comments = GoalCommentSerializer(many=True, read_only=True)

    # comments = GoalCommentSerializer(many=True,
    #                                  queryset=GoalComment.objects.filter(user_id=self.context["request"].user.pk))

    # Goal.objects.filter(user_id=self.request.user.pk,
    #                     category__is_deleted=False,
    #                     comments=GoalComment.objects.filter(user_id=self.request.user.pk)
    #                     ).exclude(status=Goal.Status.archived)
    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"

    # Проверяем, что пользователь может назначить категорию только из своих актуальных категорий.
    # Если категория выбрана как пустая, то ей назначается Категория=Default по умолчанию.
    def validate_category(self, value):
        if value is not None:
            if value.is_deleted:
                raise serializers.ValidationError("User is prohibited to assign deleted categories for goals.")

            # проверяем, что категория создаваемой цели принадлежит пользователю,
            # т.е. пользователь не может создать цель в чужой категории
            if value.user != self.context["request"].user:
                raise serializers.ValidationError("User is not owner of this category.")
        else:
            value = GoalCategory.objects.create(title="Default", user=self.context["request"].user)

        return value

    def validate_due_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

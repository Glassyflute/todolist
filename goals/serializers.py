from datetime import *
from django.utils import timezone
from rest_framework import serializers

from core.serializers import UserProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Категории создает категорию, учитывая текущего пользователя.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"


class GoalCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для Категории выводит информацию по категории или списку категорий. Для вывода данных по пользователю
    используется сериализатор Пользователя, убрана логика с подстановкой текущего пользователя в поле user.
    """
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Комментария создает комментарий к цели, учитывая текущего пользователя. Встроенные проверки по
    цели гарантируют, что пользователь может создать комментарий только к своим актуальным (не удаленным) целям.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_goal(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("User is prohibited to comment on deleted goals.")

        if value.user != self.context["request"].user:
            raise serializers.ValidationError("User is not owner of this goal.")

        return value


class GoalCommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Комментария выводит информацию по комментарию или списку комментариев. Для вывода данных по
    пользователю используется сериализатор Пользователя, убрана логика с подстановкой текущего пользователя в поле user.
    """
    user = UserProfileSerializer(read_only=True)
    goal = serializers.SerializerMethodField()

    def get_goal(self, goalcomment):
        return goalcomment.goal.title

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class GoalCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Цели создает цель, учитывая текущего пользователя. Встроенные проверки по
    категории как полю модели Цель гарантируют, что пользователь может назначить категорию только из своих актуальных
    (не удаленных) категорий. Если категория остается пустой при создании, то ей назначается Категория=Default по
    умолчанию. Проверка по дате дедлайна не позволяет указывать дату в прошлом в качестве дедлайна для цели.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    goalcomment = serializers.SerializerMethodField()

    def get_goalcomment(self, goal):
        return [item.text for item in goal.goal_comment.all()]

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"

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
        if value:
            if value < timezone.now():
                raise serializers.ValidationError("Due date cannot be in the past.")
        return value


class GoalSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Цели выводит информацию по цели или списку целей. Для вывода данных по пользователю используется
    сериализатор Пользователя, убрана логика с подстановкой текущего пользователя в поле user. Встроенные проверки по
    категории как полю модели Цель гарантируют, что пользователь может назначить категорию только из своих актуальных
    (не удаленных) категорий. Если категория остается пустой при создании, то ей назначается Категория=Default по
    умолчанию. Проверка по дате дедлайна не позволяет указывать дату в прошлом в качестве дедлайна для цели.
    """
    user = UserProfileSerializer(read_only=True)
    goalcomment = serializers.SerializerMethodField()

    def get_goalcomment(self, goal):
        return [item.text for item in goal.goal_comment.all()]

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"

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
        if value:
            if value < timezone.now():
                raise serializers.ValidationError("Due date cannot be in the past.")
        return value

from datetime import *
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from core.models import User
from core.serializers import UserProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


# Board
class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "board")


class BoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        read_only_fields = ("id", "created", "updated", "is_deleted")
        fields = "__all__"


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        read_only_fields = ("id", "created", "updated", "is_deleted")
        fields = "__all__"


class BoardSerializer(serializers.ModelSerializer):
    participants = BoardParticipantSerializer(many=True)

    class Meta:
        model = Board
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "is_deleted")

    def update(self, instance: Board, validated_data: dict) -> Board:
        with transaction.atomic():
            # удаляем текущих участников выбранной доски, не затрагивая текущего пользователя /владельца доски
            BoardParticipant.objects.filter(board=instance).exclude(user=self.context["request"].user).delete()

            # пересоздаем участников выбранной доски на основе данных, получаемых при обновлении,
            # назначая актуальные роли участников
            for participant in validated_data.pop("participants", []):
                new_participant = BoardParticipant.objects.create(board=instance, user=participant["user"],
                                                                  role=participant["role"])
            if title := validated_data.get("title"):
                instance.title = title
                instance.save(update_fields=["title"])

        return instance


# GoalCategory
class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Категории создает категорию, учитывая текущего пользователя.
    Проверка на роль создающего реализована в классе GoalCategoryPermissions в файле goals/permissions.py. Действие
    разрешено для ролей "владелец" или "редактор".
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "is_deleted")
        fields = "__all__"


class GoalCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для Категории выводит информацию по категории или списку категорий. Для вывода данных по пользователю
    используется сериализатор Пользователя, убрана логика с подстановкой текущего пользователя в поле user.
    Ограничения на действия, кроме просмотра, реализованы в классе GoalCategoryPermissions в файле
    goals/permissions.py. Класс GoalCategoryPermissions добавляет фильтр по разрешенным ролям пользователя, если
    request.method не равен GET.
    """
    user = UserProfileSerializer(read_only=True)
    board = serializers.SerializerMethodField()

    def get_board(self, goalcategory):
        return goalcategory.board.title

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "is_deleted")


# GoalComment
class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Комментария создает комментарий к цели, учитывая текущего пользователя. Встроенные проверки по
    цели гарантируют, что пользователь может создать комментарий только к своим актуальным (не удаленным) целям.
    Проверка на роль создающего и разрешенные действия реализована в классе GoalCommentPermissions в файле
    goals/permissions.py, а также внутри метода def validate_goal данного класса.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_goal(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("User is prohibited to comment on deleted goals.")

        if not BoardParticipant.objects.filter(
            user_id=self.context["request"].user.id,
            board_id=value.category.board_id,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exists():
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
        read_only_fields = ("id", "created", "updated", "user", "goal")
        fields = "__all__"


# Goal
class GoalCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Цели создает цель, учитывая текущего пользователя. Встроенные проверки по
    категории как полю модели Цель гарантируют, что пользователь может назначить категорию только из своих актуальных
    (не удаленных) категорий. Если категория остается пустой при создании, то ей назначается Категория=Default по
    умолчанию. Проверка по дате дедлайна не позволяет указывать дату в прошлом в качестве дедлайна для цели.
    Проверка на роль создающего реализована в классе GoalPermissions в файле goals/permissions.py. Действие разрешено
    для ролей "владелец" или "редактор".
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "is_deleted", "user")
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
        read_only_fields = ("id", "created", "updated", "is_deleted")
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

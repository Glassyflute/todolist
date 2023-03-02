from datetime import *

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from core.models import User
from core.serializers import UserProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


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




#####################################################
# class BoardParticipantSerializer(serializers.ModelSerializer):
#     role = serializers.ChoiceField(required=True, choices=BoardParticipant.editable_choices)
#     user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())
#
#     class Meta:
#         model = BoardParticipant
#         fields = "__all__"
#         read_only_fields = ("id", "created", "updated", "board")



# class BoardCreateSerializer(serializers.ModelSerializer):
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = Board
#         read_only_fields = ("id", "created", "updated")
#         fields = "__all__"
#
#     def create(self, validated_data):
#         user = validated_data.pop("user")
#         board = Board.objects.create(**validated_data)
#         # при создании доски сразу создаем BoardParticipant с ролью владельца
#         BoardParticipant.objects.create(user=user, board=board, role=BoardParticipant.Role.owner)
#         return board
#
#
# class BoardListSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Board
#         # read_only_fields = ("id", "created", "updated")
#         fields = "__all__"
#
#
# class BoardSerializer(serializers.ModelSerializer):
#     participants = BoardParticipantSerializer(many=True)
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = Board
#         fields = "__all__"
#         read_only_fields = ("id", "created", "updated")
#
#     def update(self, instance, validated_data):
#         owner = validated_data.pop("user")
#         old_participants = instance.participants.exclude(user=owner)
#
#         new_participants = validated_data.pop("participants")
#         new_by_username = {participant["user"]: participant for participant in new_participants}
#
#         with transaction.atomic():
#             for old_participant in old_participants:
#                 # удаляем неактуальных участников доски, не затрагивая текущего пользователя /владельца доски
#                 if old_participant["user"] not in new_by_username:
#                     old_participant.delete()
#                 else:
#                     # работаем с уже существующими участниками доски по изменениям их ролей, не затрагивая текущего
#                     # пользователя /владельца доски
#                     for participant_dict in new_by_username.values():
#                         if participant_dict["user"] == old_participant["user"]:
#                             old_participant["role"] = participant_dict["role"]
#                             old_participant.save()
#
#                     new_by_username.pop(old_participant["user"])
#
#             for new_participant_dict in new_by_username.values():
#                 BoardParticipant.objects.create(user=new_participant_dict["user"], role=new_participant_dict["role"],
#                                                 board=instance)
#             if validated_data["title"]:
#                 instance.title = validated_data["title"]
#             instance.save()
#
#         return instance




        # guidance below
        # owner = validated_data.pop("user")
        # old_participants = instance.participants.exclude(user=owner)
        #
        # new_participants = validated_data.pop("participants")
        # new_by_id = {part["user"].id: part for part in new_participants}    # ???
        #
        # with transaction.atomic():
        #     for old_participant in old_participants:
        #         if old_participant.user_id not in new_by_id:
        #             old_participant.delete()
        #         else:
        #             if (old_participant.role != new_by_id[old_participant.user_id]["role"]):
        #                 old_participant.role = new_by_id[old_participant.user_id]["role"]
        #                 old_participant.save()
        #             new_by_id.pop(old_participant.user_id)
        #     for new_part in new_by_id.values():
        #         BoardParticipant.objects.create(board=instance, user=new_part["user"], role=new_part["role"])
        #
        #     instance.title = validated_data["title"]
        #     instance.save()
        #
        # return instance

        # if participant["username"] not in self.instance.participants__user__username:
        #     participants = append(participants_data)

        #     board = Board.objects.save(update_fields=["participants"])

        # если текущий юзер не имеет роли Владелец, то не может удалять участников (или может?). Если он владелец, и
        # ИД для удаления - его, то тоже не может удалить себя как владельца.

        # если текущий юзер = Владелец доски, то не может изменить свою роль на не Владелец; но Владелец может изменить
        # роль других людей (на любую, даже Владелец?)


# - Необходимо реализовать возможность добавления участников.
# - Необходимо реализовать возможность удаления участников (владельцу себя удалить нельзя).
# - Необходимо реализовать возможность изменения участникам уровня доступа (кроме себя — владелец всегда остается владельцем).

##############################################
# class BoardParticipantCreateSerializer(serializers.ModelSerializer):
#     ...



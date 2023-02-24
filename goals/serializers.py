from rest_framework import serializers

from core.serializers import UserProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment


# not GoalCreateSerializer, as model =GoalCategory below
class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"


# for list and detail view of categories
class GoalCategorySerializer(serializers.ModelSerializer):
    # убрали логику с подстановкой текущего пользователя в поле user.
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")



#######################################

#################################
# POST for Comment
class GoalCommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    # проверять, что пользователь может создать комментарий только к своим актуальным целям
    def validate_goal(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("not allowed in deleted goals")

        if value.user != self.context["request"].user:
            raise serializers.ValidationError("not owner of goal")

        return value


#  list and detail view for Comments, used also for updating/deleting instance
class GoalCommentSerializer(serializers.ModelSerializer):
    # убрали логику с подстановкой текущего пользователя в поле user.
    user = UserProfileSerializer(read_only=True)
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")

    # goal можно текстом показывать



##################################
# added POST for goals
class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    # category = serializers.SerializerMethodField()
    # def get_category(self, goal):
    #     return goal.category.title

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    # проверять, что категория создаваемой цели принадлежит пользователю =не может создать цель в чужой категории
    def validate_category(self, value):
        if value is not None:
            if value.is_deleted:
                raise serializers.ValidationError("not allowed in deleted category")

            # проверяем, что категория создаваемой цели принадлежит пользователю,
            # т.е. пользователь не может создать цель в чужой категории
            if value.user != self.context["request"].user:
                raise serializers.ValidationError("not owner of category")
        else:
            value = GoalCategory.objects.create(title="Default", user=self.context["request"].user)

        return value

    # какие проблемы: дату обязательно ставить, можно вчерашним днем и тп создать дедлайн


# added list /detail for goals
class GoalSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # можно добавить вывод имени пользователя под целью
    # status, priority, category - можно текстом показывать; is_deleted не показывать или др видом
    comments = GoalCommentSerializer(many=True)

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"



##############
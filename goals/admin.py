from django.contrib import admin
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class GoalCategoryAdmin(admin.ModelAdmin):
    """
    Админка для категорий позволяет поиск по названию категории, username пользователя. Есть возможность фильтровать
    категории по статусу удалена/архивирована.
    """
    list_display = ("title", "user", "created", "updated", "is_deleted")
    search_fields = ("title", "user__username")
    list_filter = ("is_deleted",)
    readonly_fields = ("created", "updated")


admin.site.register(GoalCategory, GoalCategoryAdmin)


class GoalAdmin(admin.ModelAdmin):
    """
    Админка для целей позволяет поиск по названию и описанию цели, username пользователя. Есть возможность фильтровать
    цели по статусу, приоритету, дедлайну.
    """
    list_display = ("title", "user", "created", "updated", "description", "category",
                    "status", "priority", "due_date", "is_deleted")
    search_fields = ("title", "description", "user__username")
    list_filter = ("status", "priority", "due_date", "is_deleted")
    readonly_fields = ("created", "updated")
    fieldsets = (
        ("Информация по Цели", {
            "fields": ("title", "description", "category")
        }),
        ("Приоритет Цели", {
            "fields": ("due_date", "priority")
        }),
        ("Актуальность Цели", {
            "fields": ("status", "is_deleted")
        }),
        ("Действия пользователя", {
            "fields": ("created", "updated", "user")
        }),
    )


admin.site.register(Goal, GoalAdmin)


class GoalCommentAdmin(admin.ModelAdmin):
    """
    Админка для комментариев позволяет поиск по тексту комментария к цели, username пользователя, названию цели.
    """
    list_display = ("text", "goal", "user", "created", "updated")
    search_fields = ("text", "user__username", "goal__title")
    readonly_fields = ("created", "updated")
    fieldsets = (
        (None, {
            "fields": ("goal", "text", "user", "created", "updated")
        }),
    )


admin.site.register(GoalComment, GoalCommentAdmin)



###################################################################
# class BoardAdmin(admin.ModelAdmin):
#     """
#     Админка для досок позволяет поиск по названию доски. Есть возможность фильтровать доски по статусу
#     удалена/архивирована.
#     """
#     list_display = ("title", "user__username", "created", "updated", "is_deleted")
#     search_fields = ("title", "user__username", "participants__user__username")
#     list_filter = ("is_deleted",)
#     readonly_fields = ("created", "updated")
#
#
# admin.site.register(Board, BoardAdmin)


# class BoardParticipantAdmin(admin.ModelAdmin):
#     """
#     Админка для BoardParticipant позволяет поиск по xxxxxxxx. Есть возможность фильтровать xxxxx по xxxxx.
#     """
#     list_display = ("user", "created", "updated", "is_deleted")
#     search_fields = ("user__username", "role", "board")
#     list_filter = ("is_deleted",)
#     readonly_fields = ("created", "updated")
#
#
# admin.site.register(BoardParticipant, BoardParticipantAdmin)

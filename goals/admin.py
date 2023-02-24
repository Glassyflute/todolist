from django.contrib import admin
from goals.models import GoalCategory, Goal, GoalComment


# админка для категорий
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated")
    search_fields = ("title", "user")
    # нет поиска в админке по вхождению строки или точному имени автора
    list_filter = ("user", "title", "is_deleted")
    readonly_fields = ("created", "updated")


admin.site.register(GoalCategory, GoalCategoryAdmin)


# админка для целей

class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated", "description", "category",
                    "status", "priority", "deadline", "is_deleted")
    search_fields = ("title", "user", "description", "category")
    # by title == Related Field got invalid lookup: icontains. http://127.0.0.1/admin/goals/goal/?q=2
    # error also == by user, desc, ...
    list_filter = ("user", "category", "status", "priority", "deadline", "is_deleted")
    # remove filter for == user, category
    readonly_fields = ("created", "updated")
    fieldsets = (
        ("Информация по Цели", {
            "fields": ("title", "description", "category")
        }),
        ("Приоритет Цели", {
            "fields": ("deadline", "priority")
        }),
        ("Актуальность Цели", {
            "fields": ("status", "is_deleted")
        }),
        ("Действия пользователя", {
            "fields": ("created", "updated", "user")
        }),
        ("Комментарии пользователя", {
            "fields": ("comments",)
        }),
    )


admin.site.register(Goal, GoalAdmin)


# админка для комментариев
class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ("text", "goal", "user", "created", "updated")
    search_fields = ("text", "user", "goal")
    # error as above
    list_filter = ("user", "goal")
    readonly_fields = ("created", "updated")
    fieldsets = (
        (None, {
            "fields": ("goal", "text", "user", "created", "updated")
        }),
    )


admin.site.register(GoalComment, GoalCommentAdmin)

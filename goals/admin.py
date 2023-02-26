from django.contrib import admin
from goals.models import GoalCategory, Goal, GoalComment


# админка для категорий
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated", "is_deleted")
    search_fields = ("title", "user__username")
    list_filter = ("is_deleted",)
    readonly_fields = ("created", "updated")


admin.site.register(GoalCategory, GoalCategoryAdmin)


# админка для целей
class GoalAdmin(admin.ModelAdmin):
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


# админка для комментариев
class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ("text", "goal", "user", "created", "updated")
    search_fields = ("text", "user__username", "goal__title")
    # list_filter = ("goal",)
    readonly_fields = ("created", "updated")
    fieldsets = (
        (None, {
            "fields": ("goal", "text", "user", "created", "updated")
        }),
    )


admin.site.register(GoalComment, GoalCommentAdmin)

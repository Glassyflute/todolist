from django.contrib import admin

from bot.models import TgUser


class TgUserAdmin(admin.ModelAdmin):
    """
    Админка для модели пользователя Телеграм (TgUser) позволяет поиск по username для пользователя Телеграм или username
    для пользователя в БД. Есть возможность фильтровать данные по username для пользователя Телеграм.
    """
    list_display = ("tg_chat_id", "tg_username", "verification_code")
    search_fields = ("tg_username", "user__username")
    list_filter = ("tg_username", "tg_chat_id")
    readonly_fields = ("tg_chat_id", "verification_code")


admin.site.register(TgUser, TgUserAdmin)

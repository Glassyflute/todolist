from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Админка для пользователя позволяет поиск по username пользователя, емейлу, имени и фамилии. Есть возможность
    фильтровать данные по параметрам 'is_staff', 'is_active', 'is_superuser'.
    """
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    readonly_fields = ('last_login', 'date_joined')
    fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name',
                       'email', 'is_staff', 'is_active', 'date_joined', 'last_login')
        }),
    )


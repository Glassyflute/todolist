from django.db import models
from django.utils.crypto import get_random_string

from core.models import User
from goals.models import Goal, GoalCategory


class TgUser(models.Model):
    """
    Модель TgUser консолидирует информацию по пользователю из БД и пользователю в Телеграм, идентификатору чата с
    пользователем Телеграм, сохраняет код верификации для связывания пользователя из БД с его Телеграм аккаунтом.
    Методы модели включают обеспечение работы с кодом верификации и выгрузку информации из БД по целям и категориям
    пользователя.
    """
    tg_chat_id = models.BigIntegerField(verbose_name="Чат Телеграм", unique=True)
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    verification_code = models.CharField(verbose_name="Код верификации пользователя", max_length=50,
                                         null=True, blank=True, default=None)
    tg_username = models.CharField(max_length=40, verbose_name="Пользователь Телеграм", unique=True, null=True,
                                   blank=True, default=None)

    @staticmethod
    def _generate_verification_code() -> str:
        code = get_random_string(length=50, allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789")
        return code

    def show_user_goals(self):
        user_goals = Goal.objects.filter(category__board__participants__user=self.user,
                                         category__is_deleted=False).exclude(status=Goal.Status.archived)
        return user_goals

    def show_user_goal_categories(self):
        user_categories = GoalCategory.objects.filter(board__participants__user=self.user, is_deleted=False)
        return user_categories

    def assign_verification_code(self) -> str:
        verification_code = self._generate_verification_code()
        self.verification_code = verification_code
        self.save(update_fields=["verification_code"])
        return verification_code

    def assign_tg_username(self, username) -> str:
        self.tg_username = username
        self.save(update_fields=["tg_username"])
        return username

    class Meta:
        verbose_name = 'Пользователь Телеграм'
        verbose_name_plural = 'Пользователи Телеграм'
        ordering = ["-id"]

    def __str__(self):
        return f"Чат id: {self.tg_chat_id}, username пользователя в Телеграм: {self.tg_username}"


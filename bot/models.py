from django.db import models

from core.models import User


# tg_id and/or tg_username +  verification_code +  user_id from db + tg_chat_id?

class TgUser(models.Model):
    tg_chat_id = models.BigIntegerField(verbose_name="Чат Телеграм", unique=True)
    db_user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE,
                                   null=True, blank=True, default=None)
    verification_code = models.CharField(verbose_name="Код верификации пользователя", max_length=50,
                                         null=True, blank=True, default=None)
    # verification_code нужно генерировать случайным образом

    # неясно, нужен ли ИД Телеграмного юзера
    tg_user_id = models.BigIntegerField(verbose_name="Пользователь Телеграм", unique=True)
    # tg_username in serializer?????

    class Meta:
        verbose_name = 'Пользователь Телеграм'
        verbose_name_plural = 'Пользователи Телеграм'
        ordering = ["-id"]

    def __str__(self):
        return f"<Чат id: {self.tg_chat_id}>, id пользователя в Телеграм: {self.tg_user_id}"

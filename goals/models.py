from django.db import models
from django.utils import timezone

from core.models import User


class DatesModelMixin(models.Model):
    created = models.DateTimeField(verbose_name="Дата создания")
    updated = models.DateTimeField(verbose_name="Дата последнего обновления")

    class Meta:
        abstract = True
        # Для абстрактного класса не создается таблица в БД

    def save(self, *args, **kwargs):
        if not self.id:  # Когда модель только создается – у нее нет id
            self.created = timezone.now()
        self.updated = timezone.now()  # Каждый раз, когда вызывается save, проставляем свежую дату обновления
        return super().save(*args, **kwargs)


class GoalCategory(DatesModelMixin):
    title = models.CharField(verbose_name="Название", max_length=255)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return f"<{self.user.username}>: {self.title}"


class Goal(DatesModelMixin):
    class Status(models.IntegerChoices):
        to_do = 1, "К выполнению"
        in_progress = 2, "В процессе"
        done = 3, "Выполнено"
        archived = 4, "Архив"

    class Priority(models.IntegerChoices):
        low = 1, "Низкий"
        medium = 2, "Средний"
        high = 3, "Высокий"
        critical = 4, "Критический"

    title = models.CharField(verbose_name="Название", max_length=255)
    description = models.TextField(verbose_name="Описание", max_length=1000, null=True, blank=True)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    # При удалении категории Цель не удаляется, Пользователь может назначить новую Категорию для Цели.
    category = models.ForeignKey(GoalCategory, verbose_name="Категория", related_name="goals",
                                 on_delete=models.SET_NULL, null=True)
    status = models.PositiveSmallIntegerField(verbose_name="Статус", choices=Status.choices, default=Status.to_do)
    priority = models.PositiveSmallIntegerField(
        verbose_name="Приоритет", choices=Priority.choices, default=Priority.medium
    )
    due_date = models.DateTimeField(verbose_name="Дата дедлайна", null=True, blank=True)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    # comments = models.ManyToManyField("GoalComment", related_name="comments_for_goal")

    class Meta:
        verbose_name = "Цель"
        verbose_name_plural = "Цели"

    def __str__(self):
        return f"<{self.user.username}>: {self.title}"


class GoalComment(DatesModelMixin):
    # комментарии удаляются полностью при удалении Пользователя или Цели, не сохраняются в БД.
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, verbose_name="Цель", on_delete=models.CASCADE, related_name="goal_comment")
    text = models.TextField(verbose_name="Текст комментария", max_length=1000)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"<{self.user.username}>: {self.text}"

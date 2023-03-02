from django.db import models
from django.utils import timezone

from core.models import User


class DatesModelMixin(models.Model):
    """
    Класс DatesModelMixin присваивает дату создания при создании модели и обновляет дату обновления при каждом
    обновлении модели. Для абстрактного класса DatesModelMixin не создается таблица в БД.
    """
    created = models.DateTimeField(verbose_name="Дата создания")
    updated = models.DateTimeField(verbose_name="Дата последнего обновления")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        return super().save(*args, **kwargs)


class GoalCategory(DatesModelMixin):
    """
    Класс Категория создается пользователем.
    """
    board = models.ForeignKey("Board", verbose_name="Доска", on_delete=models.PROTECT, related_name="categories")
    title = models.CharField(verbose_name="Название", max_length=255)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return f"<{self.user.username}>: {self.title}"


class Goal(DatesModelMixin):
    """
    Класс Цель создается пользователем в соответствии с указанными полями, включая поле Категория.
    """
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

    class Meta:
        verbose_name = "Цель"
        verbose_name_plural = "Цели"

    def __str__(self):
        return f"<{self.user.username}>: {self.title}"


class GoalComment(DatesModelMixin):
    """
    Класс Комментарий создается пользователем к выбранной цели. Комментарии удаляются полностью при удалении
    Пользователя или Цели, не сохраняются в БД.
    """
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, verbose_name="Цель", on_delete=models.CASCADE, related_name="goal_comment")
    text = models.TextField(verbose_name="Текст комментария", max_length=1000)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"<{self.user.username}>: {self.text}"


class Board(DatesModelMixin):
    """
    Класс Доска создается пользователем. Пользователи могут участвовать в нескольких досках.
    """
    title = models.CharField(verbose_name="Название", max_length=255)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    class Meta:
        verbose_name = "Доска"
        verbose_name_plural = "Доски"

    def __str__(self):
        return f"{self.title}"


class BoardParticipant(DatesModelMixin):
    """
    Класс BoardParticipant создает набор уникальных комбинаций по значениям в паре "board" и "user" с помощью
    unique_together в классе Meta. Роли участников доски определены в классе Role.
    """
    class Role(models.IntegerChoices):
        owner = 1, "Владелец"
        writer = 2, "Редактор"
        reader = 3, "Читатель"

    board = models.ForeignKey(Board, verbose_name="Доска", on_delete=models.PROTECT, related_name="participants")
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.PROTECT, related_name="participants")
    role = models.PositiveSmallIntegerField(verbose_name="Роль", choices=Role.choices, default=Role.owner)

    class Meta:
        unique_together = ("board", "user")
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

    def __str__(self):
        return f"{self.user} с ролью {self.role} включен в доску {self.board}"

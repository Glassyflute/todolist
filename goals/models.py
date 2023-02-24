from django.db import models
from django.utils import timezone

from core.models import User


class DatesModelMixin(models.Model):
    class Meta:
        abstract = True  # Помечаем класс как абстрактный – для него не будет таблички в БД

    created = models.DateTimeField(verbose_name="Дата создания")
    updated = models.DateTimeField(verbose_name="Дата последнего обновления")

    def save(self, *args, **kwargs):
        if not self.id:  # Когда модель только создается – у нее нет id
            self.created = timezone.now()
        self.updated = timezone.now()  # Каждый раз, когда вызывается save, проставляем свежую дату обновления
        return super().save(*args, **kwargs)


class GoalCategory(DatesModelMixin):
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    title = models.CharField(verbose_name="Название", max_length=255)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    # когда удален (разлогинен) юзер, категория остается?
    ###### запретить удалять юзера, пока у него есть какая-ниб категория (созданная им)?
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    # created = models.DateTimeField(verbose_name="Дата создания")
    # updated = models.DateTimeField(verbose_name="Дата последнего обновления")
    #
    # def save(self, *args, **kwargs):
    #     if not self.id:  # Когда объект только создается, у него еще нет id
    #         self.created = timezone.now()  # проставляем дату создания
    #     self.updated = timezone.now()  # проставляем дату обновления
    #     return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


############################################################





#############################################################
# классы enum types Status, Priority поместить внутрь класса Цель?
# или наследоваться от Статуса и Приоритета?
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


class Goal(DatesModelMixin):
    title = models.CharField(verbose_name="Название", max_length=255)
    description = models.TextField(verbose_name="Описание", max_length=1000, null=True, blank=True)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    category = models.ForeignKey(GoalCategory, verbose_name="Категория", on_delete=models.SET_NULL, null=True)
    ######### если категорию хотят удалить, то можно, а Цель остается, не удаляется.

    status = models.PositiveSmallIntegerField(verbose_name="Статус", choices=Status.choices, default=Status.to_do)
    priority = models.PositiveSmallIntegerField(
        verbose_name="Приоритет", choices=Priority.choices, default=Priority.medium
    )
    deadline = models.DateTimeField(verbose_name="Дата дедлайна")

    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)
    comments = models.ManyToManyField("GoalComment", related_name="goal_w_comments")
    # created = models.DateTimeField(verbose_name="Дата создания")
    # updated = models.DateTimeField(verbose_name="Дата последнего обновления")
    #
    # def save(self, *args, **kwargs):
    #     if not self.id:  # Когда объект только создается, у него еще нет id
    #         self.created = timezone.now()  # проставляем дату создания
    #     self.updated = timezone.now()  # проставляем дату обновления
    #     return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Цель"
        verbose_name_plural = "Цели"

    def __str__(self):
        return self.title


#################
class GoalComment(DatesModelMixin):
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE)
    ######## если юзер удален, его комменты к целям тоже удаляются - CASCADE(оставлять анонимные комменты нет смысла, тк юзер создает
    # комменты только к своим собственным целям.) Анонимные комменты сущ, если есть разные юзеры, а у нас 1 юзер-владелец всего.
    ##### или SET_NULL - если юзер удален, то коммент жить без юзера не может и становится анонимным??? это если нам
    # нужен коммент. Но нам комменты не нужны, так что нет смысла.
    ### PROTECT - нельзя удалить юзера, если у юзера есть комменты к целям
    goal = models.ForeignKey(Goal, verbose_name="Цель", on_delete=models.CASCADE)
    ###### когда юзер удаляет свою Цель, то Комменты к цели также удаляются, тк комменты существуют ради Цели для юзера.
    # уже выше есть ограничение, что юзера нельзя удалить, пока у него есть Цель. Здесь цепочка тогда.

    text = models.TextField(verbose_name="Текст комментария", max_length=1000)
    # is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    # created = models.DateTimeField(verbose_name="Дата создания")
    # updated = models.DateTimeField(verbose_name="Дата последнего обновления")
    #
    # def save(self, *args, **kwargs):
    #     if not self.id:  # Когда объект только создается, у него еще нет id
    #         self.created = timezone.now()  # проставляем дату создания
    #     self.updated = timezone.now()  # проставляем дату обновления
    #     return super().save(*args, **kwargs)

    def __str__(self):
        return self.text
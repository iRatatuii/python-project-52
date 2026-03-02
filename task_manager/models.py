from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

CREATED_AT_VERBOSE = "Дата создания"
NAME_VERBOSE = "Имя"
STATUS_VERBOSE = "Статус"
LABELS_VERBOSE = "Метки"


class Status(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name=NAME_VERBOSE
    )
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name=CREATED_AT_VERBOSE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = STATUS_VERBOSE
        verbose_name_plural = "Статусы"


class Label(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name=NAME_VERBOSE
    )
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name=CREATED_AT_VERBOSE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Метка"
        verbose_name_plural = LABELS_VERBOSE


class Task(models.Model):
    name = models.CharField(max_length=150, verbose_name=NAME_VERBOSE)
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name=CREATED_AT_VERBOSE
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name=STATUS_VERBOSE,
    )

    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="authored_tasks",
        verbose_name="Автор",
    )

    executor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="executed_tasks",
        null=True,
        blank=True,
        verbose_name="Исполнитель",
    )

    labels = models.ManyToManyField(
        Label, related_name="tasks", blank=True, verbose_name=LABELS_VERBOSE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

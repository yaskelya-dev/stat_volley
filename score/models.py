from django.db import models
from players.models import Player
from stat_volley import settings
from teams.models import Team


class Friendship(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Ожидает подтверждения"
        ACCEPTED = "ACCEPTED", "Принято"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friendships_initiated",
    )
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friendships_received",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACCEPTED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Дружба"
        verbose_name_plural = "Дружба"
        unique_together = ("user", "friend")

    def __str__(self):
        return f"{self.user} -> {self.friend} ({self.status})"


class Match(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="matches",
        verbose_name="Наша команда",
    )
    opponent = models.CharField(
        max_length=100, verbose_name="Название соперника"
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата проведения")

    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"

    def __str__(self):
        return f"{self.team.name} vs {self.opponent} ({self.date.strftime('%d.%m.%Y')})"


class Set(models.Model):
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="sets",
        verbose_name="Матч",
    )
    set_number = models.PositiveSmallIntegerField(verbose_name="Номер партии")

    class Meta:
        verbose_name = "Партия"
        verbose_name_plural = "Партии"
        unique_together = ("match", "set_number")

    def __str__(self):
        return f"Партия {self.set_number} — {self.match}"


class StatAspect(models.Model):
    """Справочник действий (приём, подача, атака...)"""
    code = models.CharField(
        max_length=30, unique=True, verbose_name="Уникальный код"
    )
    name = models.CharField(max_length=50, verbose_name="Название действия")

    class Meta:
        verbose_name = "Действие статистики"
        verbose_name_plural = "Действия статистики"

    def __str__(self):
        return self.name


class StatGrade(models.Model):
    """Справочник оценок (#, +, !, -, =) для конкретного действия"""
    aspect = models.ForeignKey(
        StatAspect,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name="Действие",
    )
    symbol = models.CharField(
        max_length=5, verbose_name="Символ оценки (#, +, !, -, =)"
    )
    description = models.CharField(max_length=255, verbose_name="Описание")
    default_weight = models.FloatField(
        default=1.0, verbose_name="Вес по умолчанию (например, 0.5)"
    )

    class Meta:
        verbose_name = "Критерий оценки"
        verbose_name_plural = "Критерии оценок"

    def __str__(self):
        return f"{self.aspect.name} [{self.symbol}]"


class MatchEvent(models.Model):
    """Лог каждого действия в матче"""
    set = models.ForeignKey(
        Set,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Партия",
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name="Игрок (пусто, если ошибка соперника)",
    )
    grade = models.ForeignKey(
        StatGrade,
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="Оценка",
    )
    weight = models.FloatField(default=1.0, verbose_name="Вес действия")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Время действия"
    )

    class Meta:
        verbose_name = "Событие матча"
        verbose_name_plural = "События матчей"
        ordering = ["created_at"]

    def __str__(self):
        player_str = self.player.name if self.player else "Соперник"
        return f"{player_str} — {self.grade.aspect.name} ({self.grade.symbol})"


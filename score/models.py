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
    date = models.DateTimeField(verbose_name="Дата проведения")

    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"

    def __str__(self):
        return f"{self.team.name} vs {self.opponent} ({self.date.strftime('%d.%m.%Y')})"


class Set(models.Model):
    class ServingTeam(models.TextChoices):
        HOME = "HOME", "Мы"
        AWAY = "AWAY", "Соперник"

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="sets", verbose_name="Матч")
    set_number = models.PositiveSmallIntegerField(verbose_name="Номер партии")
    home_score = models.FloatField(default=0.0, verbose_name="Очки наши")
    away_score = models.FloatField(default=0.0, verbose_name="Очки противника")
    serving_team = models.CharField(
        max_length=10,
        choices=ServingTeam.choices,
        default=ServingTeam.HOME,
        verbose_name="Подающая команда",
    )
    is_finished = models.BooleanField(
        default=False,
        verbose_name="Партия завершена"
    )

    p1 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name="set_p1", verbose_name="Зона 1 (подача)")
    p2 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name="set_p2", verbose_name="Зона 2")
    p3 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name="set_p3", verbose_name="Зона 3")
    p4 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name="set_p4", verbose_name="Зона 4")
    p5 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name="set_p5", verbose_name="Зона 5")
    p6 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True,
                           related_name="set_p6", verbose_name="Зона 6")

    def is_lineup_complete(self):
        """Проверка, расставлены ли все 6 игроков"""
        return all([self.p1, self.p2, self.p3, self.p4, self.p5, self.p6])

    def rotate(self):
        """Ротация игроков по часовой стрелке: 1<-2<-3<-4<-5<-6<-1"""
        old_p1 = self.p1
        self.p1 = self.p2
        self.p2 = self.p3
        self.p3 = self.p4
        self.p4 = self.p5
        self.p5 = self.p6
        self.p6 = old_p1
        self.save()

    class Meta:
        verbose_name = "Партия"
        verbose_name_plural = "Партии"
        unique_together = ("match", "set_number")

    def __str__(self):
        return f"Партия {self.set_number} — {self.match}"


class StatAspect(models.Model):
    """Справочник действий (приём, подача, атака...)"""
    code = models.CharField(
        max_length=30, unique=True, verbose_name="Уникальное название: ATTACK, BLOCK"
    )
    name = models.CharField(max_length=50, verbose_name="Название действия")

    class Meta:
        verbose_name = "Действие статистики"
        verbose_name_plural = "Действия статистики"

    def __str__(self):
        return self.name


class StatGrade(models.Model):
    """Справочник оценок (#, +, !, -, =) для конкретного действия"""

    class PointEffect(models.IntegerChoices):
        OPPONENT = -1, "Очко сопернику"
        NONE = 0, "Без очка (мяч в игре)"
        OUR = 1, "Очко нашей команде"

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
    # добавил эффект на счёт
    point_effect = models.IntegerField(
        choices=PointEffect.choices,
        default=PointEffect.NONE,
        verbose_name="Влияние на счёт",
    )
    is_simple = models.BooleanField(
        default=False,
        verbose_name="Относится к простой статистике"
    )

    class Meta:
        verbose_name = "Критерий оценки"
        verbose_name_plural = "Критерии оценок"

    def __str__(self):
        return f"{self.aspect.name} [{self.symbol}] ({self.point_effect:+d})"


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


    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.grade:
            points = self.grade.point_effect * self.weight
            current_set = self.set

            if points > 0:
                current_set.home_score += points
                # ЛОГИКА ПЕРЕХОДА:
                # Если подавал соперник, а выиграли мы — мяч переходит нам (ПЕРЕХОД!)
                if current_set.serving_team == Set.ServingTeam.AWAY:
                    current_set.serving_team = Set.ServingTeam.HOME

            elif points < 0:
                current_set.away_score += abs(points)
                # Если подавали мы, а очко забил соперник — подача уходит им
                if current_set.serving_team == Set.ServingTeam.HOME:
                    current_set.serving_team = Set.ServingTeam.AWAY

            current_set.save()


    def __str__(self):
        player_str = self.player.name if self.player else "Соперник"
        return f"{player_str} — {self.grade.aspect.name} ({self.grade.symbol})"


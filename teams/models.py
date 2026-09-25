from django.db import models

from players.models import Player
from stat_volley import settings


class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teams",
        verbose_name="Владелец"
    )
    players = models.ManyToManyField(
        Player,
        through="TeamPlayer",
        related_name="teams",
        verbose_name="Состав команды"
    )

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"

    def __str__(self):
        return self.name


class TeamPlayer(models.Model):
    """ Связь команда - игрок и указание номера """
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="team_players"
    )
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="team_players"
    )
    number = models.PositiveSmallIntegerField(
        verbose_name="Игровой номер в команде"
    )

    class Meta:
        verbose_name = "Игрок в команде"
        verbose_name_plural = "Составы команд"
        unique_together = (("team", "player"), ("team", "number"))

    def __str__(self):
        return f"#{self.number} {self.player.name} ({self.team.name})"

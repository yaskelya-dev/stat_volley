import secrets
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    invite_code = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        null=True
    ) # код для добавления в совместные редакторы команды

    def generate_unique_invite_code(self):
        while True:
            code = secrets.token_urlsafe(32)
            if not CustomUser.objects.filter(invite_code=code).exists():
                return code

from django.core.management.base import BaseCommand
from score.models import StatAspect, StatGrade


class Command(BaseCommand):
    help = "Заполняет базовый справочник волейбольных действий и оценок"

    def handle(self, *args, **options):
        # Структура: code -> (name, [(symbol, description, point_effect)])
        data = {
            "PODACHA": (
                "Подача",
                [
                    ("#", "Эйс", StatGrade.PointEffect.OUR),
                    ("=", "Ошибка на подаче", StatGrade.PointEffect.OPPONENT),
                ],
            ),
            "ATTACK": (
                "Атака",
                [
                    ("#", "Забил", StatGrade.PointEffect.OUR),
                    ("=", "Ошибка в атаке", StatGrade.PointEffect.OPPONENT),
                ],
            ),
            "BLOCK": (
                "Одиночный блок",
                [
                    ("#", "Очко блоком", StatGrade.PointEffect.OUR),
                    ("=", "Ошибка на блоке", StatGrade.PointEffect.OPPONENT),
                ],
            ),
            "BLOCK_DOUBLE": (
                "Двойной блок",
                [
                    ("#", "Очко двойным блоком", StatGrade.PointEffect.OUR),
                    (
                        "=",
                        "Ошибка на двойном блоке",
                        StatGrade.PointEffect.OPPONENT,
                    ),
                ],
            ),
            "ERROR": (
                "Своя ошибка",
                [
                    (
                        "*",
                        "Любая своя ошибка",
                        StatGrade.PointEffect.OPPONENT,
                    ),
                ],
            ),
            "ERROR_OPPONENT": (
                "Ошибка соперника",
                [
                    (
                        "*",
                        "Ошибка соперника (нам очко)",
                        StatGrade.PointEffect.OUR,
                    ),
                ],
            ),
            "GOOD_OPPONENT": (
                "Удачное действие соперника",
                [
                    (
                        "*",
                        "Соперник забил (им очко)",
                        StatGrade.PointEffect.OPPONENT,
                    ),
                ],
            ),
        }

        for code, (name, grades) in data.items():
            aspect, _ = StatAspect.objects.get_or_create(
                code=code, defaults={"name": name}
            )
            for symbol, desc, effect in grades:
                StatGrade.objects.get_or_create(
                    aspect=aspect,
                    symbol=symbol,
                    defaults={"description": desc, "point_effect": effect},
                )

        self.stdout.write(
            self.style.SUCCESS("Справочник действий успешно заполнен!")
        )
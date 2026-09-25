from django import forms
from .models import Player, Team, TeamPlayer


class TeamForm(forms.ModelForm):

    class Meta:
        model = Team
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Название команды",
                }
            ),
        }
        labels = {"name": "Название команды"}


class AddPlayerToTeamForm(forms.ModelForm):
    """Форма добавления существующего игрока в конкретную команду с номером"""

    player = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Выберите игрока из базы",
    )

    class Meta:
        model = TeamPlayer
        fields = ["player", "number"]
        widgets = {
            "number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Номер (1-99)",
                    "min": 1,
                    "max": 99,
                }
            ),
        }
        labels = {"number": "Игровой номер в этой команде"}

    def __init__(self, *args, team=None, **kwargs):
        super().__init__(*args, **kwargs)
        if team:
            # Исключаем игроков, которые УЖЕ добавлены в эту команду
            self.fields["player"].queryset = Player.objects.exclude(
                id__in=team.players.values_list("id", flat=True)
            ).order_by("name")

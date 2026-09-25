from django import forms
from teams.models import Team
from .models import Match


class MatchCreateForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        label="Дата и время матча",
    )

    class Meta:
        model = Match
        fields = ["team", "opponent", "date"]
        labels = {
            "team": "Наша команда",
            "opponent": "Название соперника",
        }

from django import forms
from .models import Player


class PlayerForm(forms.ModelForm):

    class Meta:
        model = Player
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Имя и Фамилия игрока",
                }
            ),
        }
        labels = {
            "name": "Имя и Фамилия игрока",
        }

from django.urls import path
from . import views

app_name = "players"

urlpatterns = [
    path("", views.player_list_create, name="player_list"),
]

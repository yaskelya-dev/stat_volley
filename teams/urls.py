from django.urls import path
from . import views

app_name = "teams"

urlpatterns = [
    path("", views.team_list_create, name="list"),
    path("<int:team_id>/", views.team_detail, name="detail"),
    path("<int:team_id>/edit/", views.team_update, name="update"),
    path("<int:team_id>/delete/", views.team_delete, name="delete"),
    path("<int:team_id>/remove-player/<int:tp_id>/", views.remove_player_from_team, name="remove_player"),
]

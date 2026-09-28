from django.urls import path
from . import views

app_name = "players"

urlpatterns = [
    path("", views.player_list_create, name="list"),
    path("<int:pk>/edit/", views.player_edit, name="edit"),
    path("<int:pk>/delete/", views.player_delete, name="delete"),
]

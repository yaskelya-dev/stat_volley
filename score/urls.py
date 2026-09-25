from django.urls import path
from . import views

app_name = 'score'

urlpatterns = [
    path('', views.index, name='index'),
    path("new/", views.match_create, name="match_create"),
    path("<int:match_id>/live/", views.match_live, name="match_live"),
]

from django.contrib import admin
from .models import Team, TeamPlayer


class TeamPlayerInline(admin.TabularInline):
    model = TeamPlayer
    extra = 1
    autocomplete_fields = ("player",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "get_players_count")
    list_filter = ("owner",)
    search_fields = ("name", "owner__username")
    inlines = (TeamPlayerInline,)

    @admin.display(description="Кол-во игроков")
    def get_players_count(self, obj):
        return obj.players.count()


@admin.register(TeamPlayer)
class TeamPlayerAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "number", "player")
    list_filter = ("team",)
    search_fields = ("player__name", "team__name", "number")
    autocomplete_fields = ("team", "player")

from django.contrib import admin
from .models import Friendship, Match, MatchEvent, Set, StatAspect, StatGrade


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "friend", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "friend__username")


class SetInline(admin.TabularInline):
    model = Set
    extra = 1


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "opponent", "date", "get_sets_count")
    list_filter = ("date", "team")
    search_fields = ("team__name", "opponent")
    inlines = (SetInline,)

    @admin.display(description="Кол-во партий")
    def get_sets_count(self, obj):
        return obj.sets.count()


class MatchEventInline(admin.TabularInline):
    model = MatchEvent
    extra = 1
    autocomplete_fields = ("player", "grade")


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ("id", "match", "set_number")
    list_filter = ("set_number", "match__team")
    search_fields = ("match__team__name", "match__opponent")
    inlines = (MatchEventInline,)


class StatGradeInline(admin.TabularInline):
    model = StatGrade
    extra = 1


@admin.register(StatAspect)
class StatAspectAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")
    inlines = (StatGradeInline,)


@admin.register(StatGrade)
class StatGradeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "aspect",
        "symbol",
        "description",
        "default_weight",
    )
    list_filter = ("aspect",)
    search_fields = ("aspect__name", "symbol", "description")


@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "set",
        "get_player_name",
        "grade",
        "weight",
        "created_at",
    )
    list_filter = ("grade__aspect", "set__match")
    search_fields = ("player__name", "grade__aspect__name")
    autocomplete_fields = ("set", "player", "grade")

    @admin.display(description="Игрок")
    def get_player_name(self, obj):
        return obj.player.name if obj.player else "Ошибка соперника"

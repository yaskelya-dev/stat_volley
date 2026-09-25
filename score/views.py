from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from players.models import Player
from score.forms import MatchCreateForm
from score.models import Set, Match, StatGrade, MatchEvent
from users.decorators import login_required_message


@login_required_message(redirect_after_login='score:index')
def index(request):
    return render(request, 'score/index.html')


def match_create(request):
    """Страница создания нового матча"""
    if request.method == "POST":
        form = MatchCreateForm(request.POST)
        if form.is_valid():
            match = form.save()
            # Автоматически создаем 1-ю партию
            Set.objects.create(match=match, set_number=1)
            return redirect("score:match_live", match_id=match.id)
    else:
        form = MatchCreateForm()
    return render(request, "score/match_create.html", {"form": form})


def match_live(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Берем последнюю незавершенную партию, либо создаем 1-ю
    current_set = match.sets.filter(is_finished=False).last()
    if not current_set:
        last_finished = match.sets.filter(is_finished=True).last()
        next_num = (last_finished.set_number + 1) if last_finished else 1
        current_set = Set.objects.create(match=match, set_number=next_num)

    all_team_players = match.team.players.all()

    # Список игроков, которые ЕЩЁ НЕ на площадке
    placed_player_ids = [
        p.id for p in [current_set.p1, current_set.p2, current_set.p3, current_set.p4, current_set.p5, current_set.p6]
        if p
    ]
    available_players = all_team_players.exclude(id__in=placed_player_ids)

    # Действия только из простой статистики
    simple_grades = StatGrade.objects.filter(is_simple=True).select_related('aspect')

    if request.method == "POST":
        action_type = request.POST.get("action_type")

        # 1. Расстановка игроков
        if action_type == "set_position":
            zone = request.POST.get("zone")
            player_id = request.POST.get("player_id")
            player = get_object_or_404(Player, id=player_id) if player_id else None

            if zone in ['p1', 'p2', 'p3', 'p4', 'p5', 'p6']:
                setattr(current_set, zone, player)
                current_set.save()

        # 2. Запись действия в матче
        elif action_type == "add_event":
            grade_id = request.POST.get("grade_id")
            player_id = request.POST.get("player_id")  # может быть None, если очко соперника

            grade = get_object_or_404(StatGrade, id=grade_id)
            player = Player.objects.filter(id=player_id).first() if player_id else None

            # Фиксируем, кто подавал ДО этого розыгрыша
            was_away_serving = (current_set.serving_team == Set.ServingTeam.AWAY)

            MatchEvent.objects.create(
                set=current_set,
                player=player,
                grade=grade,
                weight=1.0
            )

            # Изменение счета
            current_set.save()

        # 3. Ручное редактирование счёта и подающей команды
        elif action_type == "update_score":
            current_set.home_score = float(request.POST.get("home_score", 0))
            current_set.away_score = float(request.POST.get("away_score", 0))
            current_set.serving_team = request.POST.get("serving_team", Set.ServingTeam.HOME)
            current_set.save()

        # 4. Завершение партии и переход к новой
        elif action_type == "finish_set":
            current_set.is_finished = True
            current_set.save()
            Set.objects.create(match=match, set_number=current_set.set_number + 1)

        return redirect("score:match_live", match_id=match.id)

    context = {
        "match": match,
        "current_set": current_set,
        "available_players": available_players,
        "simple_grades": simple_grades,
        "events": current_set.events.select_related("player", "grade__aspect").order_by("-created_at")[:10],
    }
    return render(request, "score/match_live.html", context)

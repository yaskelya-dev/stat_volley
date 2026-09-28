from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from players.models import Player
from score.forms import MatchCreateForm
from score.models import Set, Match, StatGrade, MatchEvent
from teams.models import Team, TeamPlayer
from users.decorators import login_required_message


@login_required_message(redirect_after_login='score:index')
def index(request):
    recent_matches = Match.objects.order_by("-created_at")[:5] if hasattr(Match, 'created_at') else Match.objects.all()[
        :5]

    return render(request, 'score/index.html', {
        'recent_matches': recent_matches
    })


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
    match = get_object_or_404(Match, pk=match_id)

    # 1. Находим или создаем 1-ю партию с базовыми значениями (счет 0:0, подача по умолчанию у соперника)
    current_set, created = Set.objects.get_or_create(
        match=match,
        set_number=1,
        defaults={
            'serving_team': getattr(Set.ServingTeam, 'AWAY', 'AWAY'),
            'home_score': 0,
            'away_score': 0,
        }
    )

    # 2. Сохранение расстановки и подачи
    if request.method == "POST":
        # Сохраняем игроков
        current_set.p1_id = request.POST.get("p1") or None
        current_set.p2_id = request.POST.get("p2") or None
        current_set.p3_id = request.POST.get("p3") or None
        current_set.p4_id = request.POST.get("p4") or None
        current_set.p5_id = request.POST.get("p5") or None
        current_set.p6_id = request.POST.get("p6") or None

        # Сохраняем, кто начинает подавать
        serving_team = request.POST.get("serving_team")
        if serving_team:
            current_set.serving_team = serving_team

        current_set.save()

        messages.success(request, "Стартовый состав и первая подача сохранены!")
        return redirect("score:match_live", match_id=match.id)

    # 3. Формируем словарь текущих игроков на площадке
    players = {
        "p1": current_set.p1,
        "p2": current_set.p2,
        "p3": current_set.p3,
        "p4": current_set.p4,
        "p5": current_set.p5,
        "p6": current_set.p6,
    }

    # 4. Получаем список ID игроков, уже стоящих на площадке
    assigned_player_ids = [
        player.id for player in players.values() if player is not None
    ]

    # 5. Получаем список игроков команды, которые ЕЩЁ не в поле
    available_players = TeamPlayer.objects.filter(
        team=match.team
    ).exclude(
        player_id__in=assigned_player_ids
    ).select_related("player")

    context = {
        "match": match,
        "set": current_set,
        "players": players,
        "available_players": available_players,
    }
    return render(request, "score/match_live.html", context)

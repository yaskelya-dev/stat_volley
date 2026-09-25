from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from score.models import Friendship
from .forms import AddPlayerToTeamForm, TeamForm
from .models import Team, TeamPlayer


@login_required
def team_list_create(request):
    """Список доступных команд (свои + команды друзей) и форма создания своей команды"""
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.owner = request.user
            team.save()
            return redirect("teams:team_detail", team_id=team.id)
    else:
        form = TeamForm()

    # Доступные команды: свои команды OR команды друзей
    friends_ids = Friendship.objects.filter(
        friend=request.user, status=Friendship.Status.ACCEPTED
    ).values_list("user_id", flat=True)

    teams = (
        Team.objects.filter(Q(owner=request.user) | Q(owner_id__in=friends_ids))
        .distinct()
        .order_by("name")
    )

    return render(
        request, "teams/team_list.html", {"teams": teams, "form": form}
    )


@login_required
def team_detail(request, team_id):
    """Детальная страница команды: просмотр состава и добавление игроков с номерами"""
    team = get_object_or_404(Team, id=team_id)

    # Проверка прав доступа (владелец или друг)
    if team.owner != request.user:
        is_friend = Friendship.objects.filter(
            user=team.owner,
            friend=request.user,
            status=Friendship.Status.ACCEPTED,
        ).exists()
        if not is_friend:
            return redirect("teams:list")

    if request.method == "POST":
        add_player_form = AddPlayerToTeamForm(
            request.POST, team=team
        )
        if add_player_form.is_valid():
            team_player = add_player_form.save(commit=False)
            team_player.team = team
            team_player.save()
            return redirect("teams:detail", team_id=team.id)
    else:
        add_player_form = AddPlayerToTeamForm(team=team)

    # Состав команды с номерами
    team_players = (
        TeamPlayer.objects.filter(team=team)
        .select_related("player")
        .order_by("number")
    )

    return render(
        request,
        "teams/team_detail.html",
        {
            "team": team,
            "team_players": team_players,
            "add_player_form": add_player_form,
        },
    )

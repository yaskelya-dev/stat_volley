from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from users.decorators import login_required_message
from .forms import PlayerForm
from .models import Player


@login_required_message(redirect_after_login='players:list')
def player_list_create(request):
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.created_by = request.user
            player.save()
            return redirect("players:list")
    else:
        form = PlayerForm()

    players = Player.objects.all().order_by("name")
    context = {
        "players": players,
        "form": form
    }

    return render(
        request,
        "players/player_list.html",
        context,
    )


@login_required_message(redirect_after_login='players:list')
def player_edit(request, pk):
    player = get_object_or_404(Player, pk=pk)
    if request.method == "POST":
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect("players:list")
    else:
        form = PlayerForm(instance=player)

    return render(
        request,
        "players/player_edit.html",
        {"form": form, "player": player}
    )


@login_required_message(redirect_after_login='players:list')
@require_POST
def player_delete(request, pk):
    player = get_object_or_404(Player, pk=pk)
    player.delete()
    return redirect("players:list")

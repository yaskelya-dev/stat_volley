from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import PlayerForm
from .models import Player


@login_required
def player_list_create(request):
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.created_by = request.user
            player.save()
            return redirect("players:player_list")
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
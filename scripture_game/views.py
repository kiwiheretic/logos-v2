from __future__ import absolute_import
from django.shortcuts import render
from .models import GameGames
# Create your views here.
def games_played(request):
    games = GameGames.objects.all().order_by('-timestamp')
    for game in games:
        userlist = []
        for user in game.gameusers_set.all():
            userlist.append(user.nick)
        game.gameuserlist = userlist
    context = {'games':games}
    return render(request, 'scripture_game/games_played.html', context)

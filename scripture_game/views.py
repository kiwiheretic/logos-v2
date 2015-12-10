from __future__ import absolute_import
from django.shortcuts import render, redirect
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import GameGames, GameUsers

# Create your views here.
def index(request):
    return redirect('scripture_game.views.summary')

def summary(request):
    games = GameGames.objects.all().order_by('-timestamp')
    
    nick_stats = {}
    # Find nick with most games played
    ## TODO:  These results should really be cached
    games_qry = GameGames.objects.all()
    for game in games_qry:
        for user in game.gameusers_set.all():
            if user.nick.lower() not in nick_stats:
                nick_stats[user.nick.lower()] = {}
                this_nick = nick_stats[user.nick.lower()]
                this_nick.update({'nick':user.nick, 'games_played':0, 
                                'games_won':0})
            this_nick = nick_stats[user.nick.lower()]
            this_nick['games_played'] += 1
        if game.winner:
            win_nick = game.winner.nick 
            nick_stats[win_nick.lower()]['games_won'] += 1

    context = {'show_menu_regardless':True, 'stats':nick_stats}
    return render(request, 'scripture_game/summary.html', context)


def games_played(request):
    games = GameGames.objects.exclude(winner = None).order_by('-timestamp')
    paginator = Paginator(games, 10) # Show 10 contacts per page

    page = request.GET.get('page')

    try:
        games_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        games_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        games_list = paginator.page(paginator.num_pages)

    for game in games_list:
        userlist = []
        for user in game.gameusers_set.all():
            userlist.append(user.nick)
        game.gameuserlist = userlist
    context = {'games':games_list, 'show_menu_regardless':True}
    return render(request, 'scripture_game/games_played.html', context)

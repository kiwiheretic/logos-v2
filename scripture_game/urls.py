# urls.py
from django.conf.urls import patterns, include, url

urlpatterns = patterns('scripture_game.views',
    url(r'^$', 'index'),
    url(r'^summary$', 'summary'),
    url(r'^games_played$', 'games_played'),
)
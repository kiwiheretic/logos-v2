# urls.py
from __future__ import absolute_import
from django.conf.urls import url
import scripture_game.views

urlpatterns = [
    url(r'^$', scripture_game.views.index),
    url(r'^summary$', scripture_game.views.summary),
    url(r'^games_played$', scripture_game.views.games_played),
]

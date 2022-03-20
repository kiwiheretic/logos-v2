from __future__ import absolute_import
from django.shortcuts import render
from django.http import HttpResponse

from .models import NickHistory
from logos.models import BotsRunning
#import xmlrpclib
import logging
#import xmlrpclib
from bot.pluginDespatch import Plugin

from django.conf import settings 
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

# Create your views here.

def index(request):
    nh = NickHistory.objects.all().order_by('network', 'host_mask', 'nick')
    nicklist = []
    for rec in nh:
        if len(nicklist) > 0:
            if nicklist[-1].nick != rec.nick or \
               nicklist[-1].network != rec.network or \
               nicklist[-1].host_mask != rec.host_mask:
                nicklist.append(rec)
        else:
            nicklist.append(rec)
            
    return render(request, 'room_manage/index.html', {'nicklist':nicklist})

def site_setup(request):
    return HttpResponse("Not Implemented")
    #return render(request, 'room_manage/site_setup.html')

def user_setup(request):
    bots_running = BotsRunning.objects.all()
    bots = []
    rooms = []
#    for bot in bots_running:
#        url = "http://localhost:{}/".format(bot.rpc)
#        srv = xmlrpclib.Server(url)
#        dead = False
#        try:
#            rooms = srv.get_rooms()
#        except Exception as e:
#            logger.error("Errpr occurred when loading rooms - Contact Administrator")
    return render(request, 'room_manage/user_setup.html', {'rooms':rooms})


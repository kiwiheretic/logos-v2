# logos.views
import pdb

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core import serializers

from forms import SettingsForm
from models import BibleColours, Settings
import copy
import pickle
import socket
import logging

import xmlrpclib

from logos.settings import LOGGING
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

def root_url(request):
    if request.user.is_authenticated():
        return redirect('/accounts/profile')
    else:
        return redirect('/accounts/login/?next=%s' % request.path)

def _get_settings():
    settings = Settings.objects.all()
    d = {}
    for s in settings:
        d[s.option] = s.value
    return d
        
def _get_rpc_url():
    settings = _get_settings()
    host = settings.get('rpc_host', None)
    port = settings.get('rpc_port', None)
    url = 'http://%s:%s/' % (host,port)
    return url

@login_required()
def profile(request):
    context = {}
    return render(request, 'logos/profile.html', context) 
    
#    if request.method == 'GET':
#        settings = _get_settings()
#        host = settings.get('rpc_host', None)
#        port = settings.get('rpc_port', None)
#        form = SettingsForm(initial=settings)
#    elif request.method == 'POST':
#        form = SettingsForm(request.POST)
#        s = Settings()
#        if form.is_valid():
#            for fld in form:
#                try:
#                    obj = Settings.objects.get(option = fld.name)
#                    obj.option = fld.name
#                    obj.value = fld.value()
#                    obj.save()
#                except Settings.DoesNotExist:
#                    obj = Settings(option=fld.name, value=fld.value())
#                    obj.save()

#        settings = _get_settings()
#        host = settings.get('rpc_host', None)
#        port = settings.get('rpc_port', None)
        
#    if not host or not port:
#        context = {'form':form, 'errors': 'Missing connection parameters'}
#        return render(request, 'logos/profile.html', context)        
#    try:
#        url = _get_rpc_url()
#        srv = xmlrpclib.Server(url)
#        network = srv.get_network_name()
        
#        # Can't send/receive objects across twisted RPC, must pickle
#        nicks_pickle = srv.get_nicks_db()
#        nicks_db = pickle.loads(nicks_pickle)
        
#        rooms = nicks_db.get_rooms()
#        room_info = nicks_db.nicks_in_room
#        nicks_info = nicks_db.nicks_info
        
#        # fix a problem with the fact that templates don't
#        # like hyphenated variables in templates
#        for k in nicks_info.keys():
#            if 'bot-status' in nicks_info[k]:
#                nicks_info[k]['bot_status'] = nicks_info[k]['bot-status']
#            else:
#                nicks_info[k]['bot_status'] = False

#        context = {'network': network, 'rooms': rooms, 'rooms_info': room_info,
#                   'nicks_info': nicks_info, 'form':form}
        
#        return render(request, 'logos/profile.html', context)
#    except socket.error:
#        context = {'form':form, 'errors': 'Could not connect to Logos bot'}
#        return render(request, 'logos/profile.html', context)

@login_required()    
def bot_approval(request, req_id):
    br = BotRequests.objects.get(pk=req_id)
    

@login_required()
def bot_deny(request, req_id):
    pass


@login_required()
def bot_colours(request):
    url = _get_rpc_url()
    srv = xmlrpclib.Server(url)
    network = srv.get_network_name()
    nicks_pickle = srv.get_nicks_db()
    nicks_db = pickle.loads(nicks_pickle)
    rooms = nicks_db.get_rooms()     

    if request.method == "POST":
        room = "#" + request.POST["room"]
        network = request.POST["network"]
        data = []
        for k in request.POST.keys():
            if k not in ("room", "network", "csrfmiddlewaretoken"):
                v = request.POST[k]
                try:
                    obj = BibleColours.objects.get\
                        (network=network, room=room,
                         element=k)
                except BibleColours.DoesNotExist:
                    obj = BibleColours(network=network, room=room,
                         element=k, mirc_colour=v)
                else:
                    obj.mirc_colour = v
                obj.save()
        messages.add_message(request, messages.INFO,
                             'Colour settings for %s saved' % room)
        return HttpResponseRedirect(reverse('logos.views.bot_colours'))

    else:
       
           
        context = {'network':network, 'rooms':rooms}
        return render(request, 'logos/logos_colours.html', context)

@login_required()
def ajax_get_room_colours(request, network, room):
    try:
        room_colours = BibleColours.objects.filter\
            (network=network, room='#'+room)
    except BibleColours.DoesNotExist:
        return HttpResponse(None)

    data = serializers.serialize("json", room_colours)

    return HttpResponse(data)

@login_required()
def nicks_css(request):
    context = {}
    return render(request, 'logos/nicks_css.html', context)
    

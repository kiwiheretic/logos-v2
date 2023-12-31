# logos.views
from __future__ import absolute_import

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.core import serializers
from django.db import IntegrityError


from .forms import SettingsForm, UserSettingsForm
from .models import Settings, BotsRunning, Plugins, NetworkPlugins, RoomPlugins, NetworkPermissions, RoomPermissions
from logos.roomlib import get_user_option, set_user_option, get_global_option, set_global_option
from .pluginlib import configure_app_plugins

import copy
import re
import pickle
import socket
import logging
import inspect

import pytz
#import xmlrpclib
from bot.pluginDespatch import Plugin

from django.conf import settings 
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

# def room_settings(request):
    # context = {}
    # return render(request, 'logos/room_settings.html', context)
    
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

@login_required
def set_timezone(request, extra_ctx):
    if request.method == 'POST':
        #request.session['django_timezone'] = request.POST['timezone']
        set_user_option(request.user, 'timezone', request.POST['timezone'])
        messages.add_message(request, messages.INFO, 'Time Zone Information Saved')
        return redirect('/accounts/profile/')
    else:
        ctx = {'timezones': pytz.common_timezones}
        ctx.update(extra_ctx)
        return render(request, 'logos/preferences.html', ctx)
    
@login_required()
def preferences(request):
    ctx = {}
    if request.method == 'POST':
        set_global_option('site-name', request.POST['site-name'])
        set_global_option('tag-line', request.POST['tag-line'])
        messages.add_message(request, messages.INFO, 'Site information saved')
    else:
        site_name = get_global_option('site-name')
        if not site_name: site_name = "Set this site name in preferences"
        tag_line = get_global_option('tag-line')
        if not tag_line: tag_line = "Tag line not set"
        ctx = {'site_name':site_name, 'tag_line':tag_line}
    return set_timezone(request, ctx)


@login_required()
def user_settings(request):
    if request.method == "GET":
        trigger = get_user_option(request.user, "trigger")
        if trigger:
            form = UserSettingsForm(initial={'trigger_choice':trigger})
        else:
            form = UserSettingsForm()
    else: # POST
        form = UserSettingsForm(request.POST)
        if form.is_valid():
            trigger = form.cleaned_data['trigger_choice']
            set_user_option(request.user, 'trigger', trigger)
            messages.add_message(request, messages.INFO, 'User Trigger Successfully set to "'+trigger+'"')
            return redirect('plugins')

    return render(request, 'logos/user_settings.html', {'form':form})

@login_required()
def admin(request):
    return HttpResponseRedirect(reverse('logos.views.bots'))

@login_required()
def bots(request):
    bots_running = BotsRunning.objects.all()
    bots = []
    for bot in bots_running:
        url = "http://localhost:{}/".format(bot.rpc)
        srv = xmlrpclib.Server(url)
        dead = False
        try:
            networks = srv.get_networks()
            if request.method == "POST":
                rooms = srv.get_rooms()
                netcnt = 0
                rmcnt = 0
                for net_room in rooms:
                    network = net_room['network']
                    rooms_list = net_room['rooms']
                    try:
                        np = NetworkPermissions(network=network)
                        np.save()
                    except IntegrityError:
                        pass
                    else:
                        netcnt+=1

                    for room_dict in rooms_list:
                        try:
                            room = room_dict['room']
                            rp = RoomPermissions(network = network, room = room)
                            rp.save()
                        except IntegrityError:
                            pass
                        else:
                            rmcnt+=1
                messages.add_message(request, messages.INFO,
                     'Updated {} networks and {} room records'.format(netcnt, rmcnt))


        except Exception as e:
            print (e.errno)
            # error 111 is connection refused
            if e.errno == 10061 or e.errno == 111:
                dead = True
            else:
                raise
            networks = []
        print (networks)
        bots.append({'id': bot.id, 'pid':bot.pid, 'alive':not dead, 'rpc':bot.rpc, 'networks':networks})
    context = {'bots':bots}
    return render(request, 'logos/bots.html', context)

def bot_commands(request):
    helps = []
    for app in settings.INSTALLED_APPS:
        #import pdb; pdb.set_trace()
        try:
            plugin_mod = __import__(app + ".bot_plugin").bot_plugin
            for attr in dir(plugin_mod):
                a1 = getattr(plugin_mod, attr)
                # Check if the class is a class derived from 
                # bot.PluginDespatch.Plugin
                # but is not the base class only

                if inspect.isclass(a1) and \
                a1 != Plugin and \
                issubclass(a1, Plugin) and \
                hasattr(a1, 'plugin'):
                    # make up a bogus irc_conn object
                    class Fake_factory:
                        reactor = None
                        network = None
                        channel = None

                    class Fake_conn:
                        def __init__(self):
                            self.factory = Fake_factory()
                    # instantiate the class to inspect it
                    obj = a1(None, Fake_conn())
                    cmd_list = []
                    if obj.commands:
                        for cmd_tuple in obj.commands:
                            cmd_s = re.sub(r"\\s\+|\\s\*", ' ', cmd_tuple[0])
                            cmd_s = re.sub(r"\$$", '', cmd_s)
                            cmd_s = re.sub(r"\(\?P\<([^>]+)>[^)]+\)", r"<\1>", cmd_s)
                            cmd_s = re.sub(r"\(\?\:([a-z]+\|[a-z]+)\)", r"\1", cmd_s)
                            cmd_s = re.sub(r"\(\\d\+\)", r"<number>", cmd_s)
                            cmd_s = re.sub(r"\(\.\*\)", r"...", cmd_s)
                            descr = cmd_tuple[2]
                            cmd_list.append((cmd_s, descr))
                    helps.append(obj.plugin + (cmd_list,))

        except ImportError:
            pass
    return render(request, "logos/commands_list.html", {'cmds':helps})

def configure_plugins(plugins):
    for app in settings.INSTALLED_APPS:
        configure_app_plugins(app, plugins)


def add_new_plugins(plugins):
    for app in settings.INSTALLED_APPS:
        try:
            plugin_mod = __import__(app + ".bot_plugin").bot_plugin
            for attr in dir(plugin_mod):
                a1 = getattr(plugin_mod, attr)
                # Check if the class is a class derived from 
                # bot.PluginDespatch.Plugin
                # but is not the base class only

                if inspect.isclass(a1) and \
                a1 != Plugin and \
                issubclass(a1, Plugin) and \
                hasattr(a1, 'plugin'):
                    plugin_name = a1.plugin[0]
                    plugin_descr = a1.plugin[1]
                    if not Plugins.objects.filter(name = plugin_name).exists():
                        plugin = Plugins(name = plugin_name,
                                description = plugin_descr)
                        plugin.save()
                    break


        except ImportError:
            pass

@login_required()    
def plugins(request):
    plugins = Plugins.objects.order_by('name')
    add_new_plugins(plugins)
    configure_plugins(plugins)

    networks = []
    for plugin in plugins:
        for network in plugin.networkplugins_set.all():
            if network.network not in networks:
                networks.append(network.network)
    context = {'plugins':plugins, 'networks':networks, 'networkpermissions':NetworkPermissions}
    return render(request, 'logos/plugins.html', context)

@login_required()    
def networkplugins(request, net_plugin_id):
    plugin = get_object_or_404(NetworkPlugins, pk=net_plugin_id)
    if request.method == 'POST':
        if 'activate' in request.POST:
            if 'Activate' in request.POST['activate']:
                plugin.enabled = True
                plugin.save()
            if 'Deactivate' in request.POST['activate']:
                plugin.enabled = False
                plugin.save()
    context = {'plugin':plugin, 'networkpermissions':NetworkPermissions,
                'roompermissions':RoomPermissions}
    return render(request, 'logos/network_plugins.html', context)
    

@login_required()    
def plugin_room_activate(request, plugin_id):
    plugin = get_object_or_404(RoomPlugins, pk=plugin_id)
    if plugin.enabled:
        plugin.enabled = False
    else:
        plugin.enabled = True
    plugin.save()
    return HttpResponseRedirect(reverse('logos.views.networkplugins', args=(plugin.net.id,)))


    
@login_required()    
def deletenetworkplugins(request, network):
    if request.method == 'POST':
        if request.POST['confirm'] == 'Yes':
            NetworkPlugins.objects.filter(network = network).delete()
        return HttpResponseRedirect(reverse('logos.views.plugins'))
            
    message = 'Are you sure you wish to delete all plugin entries for "{}"'.format(network)
    context = {'network':network, 'heading':'Network Delete Confirmation',
        'detail':message}
    return render(request, 'logos/confirm.html', context)
    
@login_required()
def bot_view(request, id):
    bot = BotsRunning.objects.get(pk=id)
    url = "http://localhost:{}/".format(bot.rpc)
    srv = xmlrpclib.Server(url)
    factories = srv.get_factories()
    context = {'factories':factories, 'bot':bot}
    return render(request, 'logos/factories.html', context)
    
    
    
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
    

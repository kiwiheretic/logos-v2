from __future__ import absolute_import
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .forms import SiteSetupForm
from .models import BotNetGroups, BotNetRooms
from logos.models import RoomPlugins

def get_botnet_rooms():
    plugins = []
    rooms = []
    for plugin in RoomPlugins.objects.filter(net__plugin__name="botnet", net__enabled=True, enabled=True ).order_by('net__network', 'room'):
        if not plugins or (len(plugins) > 0 and \
        (plugins[-1].net.network != plugin.net.network or \
        plugins[-1].room != plugin.room)):
            plugins.append(plugin)
            rooms.append((plugin.id, plugin.net.network + " / " + plugin.room))
    return rooms

# Create your views here.

# TODO: Mark view as atomic when find out how
@login_required()
@transaction.atomic
def site_setup(request, group=None):
    botnet_rooms = get_botnet_rooms()
    groups = BotNetGroups.objects.all()
    if request.method == "POST":
        # The object will not exist if it is being created
        # for the first time.
        try:
            group_obj = BotNetGroups.objects.get(pk=group)
        except BotNetGroups.DoesNotExist:
            pass
        if 'delete' in request.POST:
            return render(request, 'botnet/site_setup.html', {'group':group_obj})
        elif 'delete_confirm_yes' in request.POST:
            group_obj.delete()
            messages.info(request, "Group {} deleted sucessfully".format(group_obj.group_name))
            return redirect(reverse('logos.views.plugins'))
        elif 'delete_confirm_no' in request.POST:
            messages.info(request, "Group {} not deleted".format(group_obj.group_name))
            return redirect(reverse('logos.views.plugins'))
        elif 'edit' in request.POST:
            group_name = group_obj.group_name
            active = group_obj.active
            rooms = []
            for room_obj in group_obj.botnetrooms_set.all():
                network = room_obj.network
                room = room_obj.room
                pgn = RoomPlugins.objects.get(net__plugin__name = 'botnet', 
                        room = room, net__network = network)
                rooms.append(pgn.id)
                data={'id':group_obj.id, 'group':group_name,'rooms':rooms, 'active':active}
            form = SiteSetupForm(data, choices=botnet_rooms, readonly_name=True)
        else:
            form = SiteSetupForm(request.POST, choices=botnet_rooms)
            if form.is_valid():
                group = form.cleaned_data['group']
                rooms = form.cleaned_data['rooms']
                active = form.cleaned_data['active']
                group_id = form.cleaned_data['id']
                plugins = RoomPlugins.objects.filter(id__in = rooms)
                if group_id:
                    bg = BotNetGroups.objects.get(pk=group_id)
                    bg.active = active
                    bg.botnetrooms_set.all().delete()
                else:
                    bg = BotNetGroups(group_name = group, active = active)
                    bg.save()
                for plg in plugins:
                    network = plg.net.network
                    room = plg.room
                    bnr = BotNetRooms(group = bg,
                            network = network,
                            room = room)
                    bnr.save()
                if group_id:
                    messages.info(request, "Group {} updated".format(bg.group_name))
                else:
                    messages.info(request, "Group {} created".format(bg.group_name))
                return redirect(reverse('logos.views.plugins'))
            else: # not valid
                pass # not valid
    else:
        form = SiteSetupForm(choices=botnet_rooms)
    return render(request, 'botnet/site_setup.html', {'form':form, 'rooms':botnet_rooms, 'groups':groups})



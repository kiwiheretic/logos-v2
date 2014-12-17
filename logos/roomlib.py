#roomlib.py
from logos.models import RoomOptions, Settings
from django.core.exceptions import ObjectDoesNotExist
import pdb

def set_global_option(option, value):
    try:
        obj = Settings.objects.get(option = option)
        obj.value = value
        obj.save()
    except Settings.DoesNotExist:
        obj = Settings(option=option, value=value)
        obj.save()   

def get_global_option(option):
    try:
        obj = Settings.objects.get(option = option)
        return obj.value
    except Settings.DoesNotExist:
        return None
    
def get_startup_rooms(network):
    rooms = RoomOptions.objects.filter(network=network, option='active')
    room_list = []
    for rm in rooms:
        if rm.value == '1': # Active is true
            room_list.append(rm.room)
    return room_list

def set_room_defaults(network, room, defaults):
    for option, value in defaults:
        opt = get_room_option(network, room, option)
        if not opt:
            set_room_option(network, room, option, value)

def get_room_option(network, room, opt):
    try:
        value_of_opt = RoomOptions.objects.get(network=network.lower(),
                                           room = room.lower(),
                                           option = opt).value
        return value_of_opt
    except ObjectDoesNotExist:
        return None

def set_room_option(network, room, opt, value):
    room_opt, created = RoomOptions.objects.get_or_create(network = network.lower(),
                           room = room.lower(),
                           option = opt)

    room_opt.value = value

    room_opt.save()

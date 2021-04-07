#roomlib.py
from django.core.exceptions import ObjectDoesNotExist

def set_global_option(option, value):
    """ Set a global option for a given plugin"""
    try:
        obj = Settings.objects.get(option = option)
        obj.value = value
        obj.save()
    except Settings.DoesNotExist:
        obj = Settings(option=option, value=value)
        obj.save()   

def get_global_option(option):
    """ Get a global option for a given plugin"""
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
    """ Get a room specific option for a given plugin"""
    try:
        value_of_opt = RoomOptions.objects.get(network=network.lower(),
                                           room = room.lower(),
                                           option = opt).value
        return value_of_opt
    except ObjectDoesNotExist:
        return None

def set_room_option(network, room, opt, value):
    """ Set a room specific option for a given plugin"""
    room_opt, created = RoomOptions.objects.get_or_create(network = network.lower(),
                           room = room.lower(),
                           option = opt)

    room_opt.value = value

    room_opt.save()
    

def get_user_option(user, opt, namespace="default"):
    """ Get a user specific option for a given plugin"""
    try:
        value_of_opt = UserOptions.objects.get(user = user,
                                           namespace = namespace,
                                           option = opt).value
        return value_of_opt
    except ObjectDoesNotExist:
        return None

def set_user_option(user, opt, value, namespace="default"):
    """ Set a user specific option for a given plugin"""
    user_opt, _ = UserOptions.objects.get_or_create(user = user,
                           namespace = namespace,
                           option = opt)

    user_opt.value = value

    user_opt.save()

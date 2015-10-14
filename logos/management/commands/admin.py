from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction

from logos.models import NetworkPermissions, RoomPermissions
from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm, get_perms, remove_perm, \
    get_perms

import re
import pdb

class Command(BaseCommand):
#    args = '<poll_id poll_id ...>'
#    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        largs = list(args)
        cmdname = largs.pop(0)
        cmd_method = 'cmd_%s' % (cmdname,)
        if hasattr(self, cmd_method):
            cmd = getattr(self, cmd_method)
            try:
                cmd(*largs)
            except TypeError, e:
                self.stdout.write("A type error occurred")
                self.stdout.write(e.message)
        else:
            self.stdout.write("admin command \"%s\" not found" % (cmdname,))
        

    def cmd_adduser(self, username, email, password):
        if User.objects.filter(username=username).exists():
            self.stdout.write("User %s already exists" % (username,))
        else:
            user = User.objects.create_user(username, email, password)
            user.save()
            self.stdout.write("User %s created" % (username,))

    def cmd_setpass(self, username, password):
        try:
            user = User.objects.get(username__iexact = username.lower())
        except User.DoesNotExist:
            self.stdout.write("Unknown user")
            return 
        user.set_password(password)
        user.save()       
        self.stdout.write("Password successfully changed")
        
    def cmd_listusers(self):
        for user in User.objects.all():
            self.stdout.write("%s %s" % (user.username, user.email))

    def cmd_listnetworks(self):
        for net in NetworkPermissions.objects.all():
            self.stdout.write("%s " % (net.network, ))
                

    def cmd_listperms(self):
        self.stdout.write("Network Permissions")
        for perm, desc in NetworkPermissions._meta.permissions:
            self.stdout.write("  {}, {}".format(perm, desc))
        self.stdout.write("\nRoom Permissions")
        for perm, desc in RoomPermissions._meta.permissions:
            self.stdout.write("  {}, {}".format(perm, desc))


    @transaction.atomic                                     
    def cmd_unassignperm(self, network, room, username, permission):
#        if not re.match(r"#[a-zA-Z0-9-]+", room):
#            self.stdout.write("Invalid room name {} -- cannot assign".format(room))
#            return
        
        try:
            user = User.objects.get(username__iexact = username)
        except User.DoesNotExist:
            self.stdout.write("Unknown user")
            return
        
        if room == "#":  # Single hash denotes network permission
            for perm, desc in NetworkPermissions._meta.permissions:
                if perm == permission:

                    try:
                        perm_obj = NetworkPermissions.objects.get(network=network)
                        remove_perm(permission, user, perm_obj)
                        self.stdout.write("Permission unassigned")
                    except NetworkPermissions.DoesNotExist:
                        self.stdout.write("Permission not found")
                    return
        else: # room permission
            for perm, desc in RoomPermissions._meta.permissions:
                if perm == permission:
                    try:
                        perm_obj = RoomPermissions.objects.get(network=network, room=room.lower())
                        remove_perm(permission, user, perm_obj)
                        self.stdout.write("Permission unassigned")

                    except RoomPermissions.DoesNotExist:
                        self.stdout.write("Permission not found")
                    break        
        
    @transaction.atomic                                     
    def cmd_assignperm(self, network, room, username, permission):
        assignperm(network, room, username, permission)
        
    def cmd_getperms(self, username):
        try:
            user = User.objects.get(username__iexact = username)
        except User.DoesNotExist:
            self.stdout.write("Unknown user")
            return
        
        self.stdout.write("=== Network Permissions ===")
        for net_obj in NetworkPermissions.objects.all():
            
            perms = get_perms(user, net_obj)
            self.stdout.write("{} {}".format(net_obj.network,
                                                ", ".join(perms)))
        
        self.stdout.write("\n=== Room Permissions ===")
        for room_obj in RoomPermissions.objects.all():
            perms = get_perms(user, room_obj)
            self.stdout.write("{} {} {}".format(room_obj.network,
                                                room_obj.room,
                                                ", ".join(perms)))
            

    def cmd_copyperms(self, network_old, network_new):
        perm_obj = NetworkPermissions.objects.get(network=network_old)
        if not NetworkPermissions.objects.filter(network = network_new).exists():
            obj.network = network_new
            obj.pk = None
            obj.save()
        else:
            obj = NetworkPermissions.objects.get(network = network_new)

        net_obj = NetworkPermissions.objects.get(network = network_old)
        for user in User.objects.all():
            perms = get_perms(user, net_obj)
            for perm in perms:
                assign_perm(perm, user, obj)
                

        perm_objs = RoomPermissions.objects.filter(network=network_old)
        for obj in perm_objs:
            room = obj.room
            if not RoomPermissions.objects.filter(network = network_new, room=room).exists():
                obj.network = network_new
                obj.pk = None
                obj.save()
            else:
                obj = RoomPermissions.objects.get(network = network_new, room=room)                

            net_obj = RoomPermissions.objects.get(network = network_old, room=room)
            for user in User.objects.all():
                perms = get_perms(user, net_obj)
                for perm in perms:
                    assign_perm(perm, user, obj)
        self.stdout.write("Successfully copied permissions to new network")

def assignperm(network, room, username, permission):

    if not re.match(r"#[a-zA-Z0-9-]*", room):
        self.stdout.write("Invalid room name {} -- cannot assign".format(room))
        return
    
    perm_obj = None
    
    if room == "#":  # if network permission
        for perm, desc in NetworkPermissions._meta.permissions:
            if perm == permission:

                try:
                    perm_obj = NetworkPermissions.objects.get(network=network)
                except NetworkPermissions.DoesNotExist:
                    perm_obj = NetworkPermissions(network=network)
                    perm_obj.save()
                break

    else:  # else room permission
        for perm, desc in RoomPermissions._meta.permissions:
            if perm == permission:
                try:
                    perm_obj = RoomPermissions.objects.get(network=network, room=room.lower())
                except RoomPermissions.DoesNotExist:
                    perm_obj = RoomPermissions(network=network, room=room.lower())
                    perm_obj.save()                    
                break
    if perm_obj == None:
        print("Unknown permission type")
        return
    try:
        user = User.objects.get(username__iexact = username)
    except User.DoesNotExist:
        self.stdout.write("Unknown user")
        return

    assign_perm(permission, user, perm_obj)
    print("Assigned {} permission to {} successfully".format(permission, username))


        
    
    
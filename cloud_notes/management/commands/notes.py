from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction

from cloud_notes.models import Folder
from django.contrib.auth.models import User

import re

class Command(BaseCommand):

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
        

    def cmd_initdb(self):
        for user in User.objects.all():
            try:
                Folder.objects.get(name='Main', user=user)
            except Folder.DoesNotExist:
                self.stdout.write("creating Main for %s" % (user.username,))
                folder = Folder(name = 'Main', user = user)
                folder.save()

            try:
                Folder.objects.get(name='Trash', user=user)
            except Folder.DoesNotExist:
                self.stdout.write("creating Trash for %s" % (user.username,))
                folder = Folder(name = 'Trash', user = user)
                folder.save()

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction

from cloud_memos.models import Folder
from django.contrib.auth.models import User

import re

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
        

    def cmd_initdb(self):
        for user in User.objects.all():
            try:
                Folder.objects.get(name='inbox', user=user)
            except Folder.DoesNotExist:
                self.stdout.write("creating inbox for %s" % (user.username,))
                folder = Folder(name = 'inbox', user = user)
                folder.save()

            try:
                Folder.objects.get(name='outbox', user=user)
            except Folder.DoesNotExist:
                self.stdout.write("creating outbox for %s" % (user.username,))
                folder = Folder(name = 'outbox', user = user)
                folder.save()

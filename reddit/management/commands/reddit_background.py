#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
from __future__ import absolute_import
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.utils import IntegrityError
import sys
import re
import praw
import pytz
import datetime

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from ...models import Submission, Comments
from django.contrib.sites.models import Site

from logos.roomlib import get_global_option
import logging

from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class Command(BaseCommand):
    help = 'Reddit Background Server'

    def add_arguments(self, parser):
        parser.add_argument('subcommand', nargs='?')

        # Named (optional) arguments
        parser.add_argument(
            '--port',
            action='store',
            help='port to receive packets',
        )     

    def handle(self, *args, **options):

        if options['port']:
            port = int(options['port'])
        else:
            port = 5011

        subcommand = options['subcommand']
        if subcommand:
            self.stdout.write('Nothing done')
        else:
            self.stdout.write('Starting reddit background server on port '+str(port))
            self.start_server(port)
            self.stdout.write('Reddit Background server terminated')

    def start_server(self, port):
        startReactor(port)


class RedditBackgroundServerUDP(DatagramProtocol):
    def __init__(self, *args, **kwargs):
        #super(RedditBackgroundServerUDP, self).__init__(*args, **kwargs)
        #DatagramProtocol.__init__(self, *args, **kwargs)
        self.authenticate()

    def datagramReceived(self, datagram, address):
        cmd = datagram.split(" ")[0]
        arg = re.sub("\S+ ","",datagram,count=1)
        print("cmd {} arg {}".format(cmd, arg))
        if cmd == "hello":
            self.transport.write("hello", address)
        elif cmd == "commentise":
            posts = re.split(r",\s*", arg)
            print posts
            self.commentise_posts(posts)

    def authenticate(self):
        site = Site.objects.get(pk=settings.SITE_ID)
        self.r = praw.Reddit('Heretical v0.1 by /u/kiwiheretic '
                'https://github.com/kiwiheretic/logos-v2 for source')
        consumer_key = get_global_option('reddit-consumer-key')
        consumer_secret = get_global_option('reddit-consumer-secret')
        redirect_uri = 'http://' + site.domain
        redirect_uri += '/reddit/oauth-callback/'
        self.r.set_oauth_app_info(client_id=consumer_key,
                 client_secret=consumer_secret,
                 redirect_uri=redirect_uri)

    def commentise_posts(self, posts):
        for post_id in posts:
            try:
                subrec = Submission.objects.get(pk=post_id)
                subobj = self.r.get_info(thing_id = subrec.name)
                self._traverse_comments(subrec.name, subrec, subobj.comments)
            except Submission.DoesNotExist:
                # Maybe someone just deleted it, who knows
                pass
        print "commentisation complete"

    def _traverse_comments(self, parent, submission, comments):
        for comment in comments:
            # exclude deleted comments
            if not hasattr(comment, 'author') or not comment.author: continue
            cdate = datetime.datetime.fromtimestamp(
                int(comment.created_utc)
                )
            udate = timezone.make_aware(cdate, timezone = pytz.utc)
            try:
                comm = Comments(name = comment.name,
                        submission = submission,
                        parent_thing = parent,
                        created_at = udate,
                        author = comment.author.name,
                        body = comment.body,
                        score = comment.score)
                comm.save()
                print comm.name
            except IntegrityError:
                pass

            self._traverse_comments(comment.name, submission, comment.replies)

def startReactor(port):
    reactor.listenUDP(port, RedditBackgroundServerUDP())
    reactor.run()

if __name__ == '__main__':
    startReactor(5011)

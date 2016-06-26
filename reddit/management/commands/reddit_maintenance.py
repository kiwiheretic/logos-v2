from __future__ import absolute_import
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from django.utils import timezone
from django.db.utils import IntegrityError

from logos.roomlib import get_global_option

import sys
import pytz
import praw

import datetime
from ...models import RedditCredentials, MySubreddits, Subreddits, Submission
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class Command(BaseCommand):
    help = 'Perform regular reddit database maintenance'

    def add_arguments(self, parser):
        parser.add_argument('subcommand', nargs='?')
        parser.add_argument('--port', type=int, action='store')
        

    def handle(self, *args, **options):
        subcommand = options['subcommand']
        if subcommand:
            self.stdout.write('Nothing done')
        else:
            if options['port']:
                port = options['port']
            else:
                port = None

            self.reddit_maintenance(port)
            self.stdout.write('Successfully finished reddit maintenance.')

    def reddit_maintenance(self, port):
        self.authenticate(port)
        self.my_subreddits()
        self.get_submissions()

    def authenticate(self, port):
        site = Site.objects.get(pk=settings.SITE_ID)
        self.r = praw.Reddit('Heretical v0.1 by /u/kiwiheretic '
                'https://github.com/kiwiheretic/logos-v2 for source')
        consumer_key = get_global_option('reddit-consumer-key')
        consumer_secret = get_global_option('reddit-consumer-secret')
        redirect_uri = 'http://' + site.domain
        if port:
            redirect_uri += ":"+str(port)
        redirect_uri += '/reddit/oauth-callback/'
        self.r.set_oauth_app_info(client_id=consumer_key,
                 client_secret=consumer_secret,
                 redirect_uri=redirect_uri)

    def get_submissions(self):
        for subr in Subreddits.objects.all():
            sr = self.r.get_subreddit(subr.display_name)
            for sub in sr.get_new(limit=100):
                # Don't save deleted posts (ie. author is blank)
                # https://www.reddit.com/r/redditdev/comments/1630jj/praw_is_returning_postauthorname_errors/c7s8zx9
                if not sub.author: continue

                cdate = datetime.datetime.fromtimestamp(
                                int(sub.created_utc)
                                    )
                udate = timezone.make_aware(cdate, timezone = pytz.utc)
                print sub.name, udate, sub.num_comments, repr(sub.title)
                try:
                    post = Submission(name = sub.name,
                            created_at = udate,
                            subreddit = subr,
                            title = sub.title,
                            author = sub.author,
                            body = sub.selftext,
                            url = sub.url,
                            score = sub.score,
                            link_flair_text = sub.link_flair_text,
                            num_comments = sub.num_comments)
                    post.save()
                except IntegrityError:
                    if Submission.objects.filter(name = sub.name).exists():
                        print "{} already exists".format(sub.name)
                    else:
                        print "Error: Could not insert {} {}".format(sub.name, sub.title)
                        import pdb; pdb.set_trace()

    def my_subreddits(self):
        for cred in RedditCredentials.objects.all():
            access = cred.credentials()
            self.r.set_access_credentials(**access)
            authenticated_user = self.r.get_me()
            print authenticated_user.name, authenticated_user.link_karma
            try:
                mysubs = MySubreddits.objects.get(user=cred.user)
                # remove all subreddit subscriptions
                # we will repopulate them afresh
                mysubs.subreddits.clear()
            except MySubreddits.DoesNotExist:
                pass

            for sub in self.r.get_my_subreddits():
                print sub.name, sub.display_name, sub.url
                obj, _ = Subreddits.objects.get_or_create(name = sub.name,
                        defaults = {'display_name':sub.display_name,
                            'url' : sub.url})
                mysub, _ = MySubreddits.objects.get_or_create(user = cred.user)
                mysub.subreddits.add(obj)

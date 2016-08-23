# test plugin
from __future__ import absolute_import
from twisted.internet import task
from bot.pluginDespatch import Plugin
import re
from datetime import datetime, timedelta
import time
import pytz
import logging
import praw
from logos.constants import REDDIT_UA
from .models import FeedSub, FeedProgress, Submission, Subreddits
from logos.models import RoomPermissions
from bot.logos_decorators import login_required, irc_room_permission_required
from logos.roomlib import get_global_option, set_global_option, \
    get_room_option, set_room_option
from django.utils import timezone
from django.db.models import Min, Q

from django.contrib.auth.models import User
from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

FEED_CHECK_TIME = 10*60 # in seconds

class RedditPlugin(Plugin):
    plugin = ("reddit", "Reddit Feed Module")
    def __init__(self, *args, **kwargs):
        super(RedditPlugin, self).__init__(*args, **kwargs)
        
        self.commands = (\
         #(r'add subreddit (?P<room>#\S+)(?P<subreddit>/r/[a-zA-Z0-9]+$', self.add_subreddit, "Add a subreddit subscription for room"),
         (r'add subreddit /r/(?P<subreddit>[a-zA-Z0-9]+)$', self.add_subreddit, "Add a subreddit subscription for room"),
         (r'remove subreddit (?P<id>\d+)$', self.remove_subreddit, "remove a subreddit subscription"),
         (r'list subreddits$', self.list_subreddits, "List all feeds"),
         (r'reset feeds$', self.reset_feeds, "Reset feeds for current room"),
         (r'pull feeds$', self.pull_feeds, "List all feeds"),
         (r'get feed (?P<id>\d+)$', self.get_feed, "get a feed"),
         (r'set (?P<room>#[a-zA-Z0-9-]+) feed display limit (?P<count>\d+)',
           self.set_feed_limit, 
          'Set number of messages per feed to display each time in room'), 
         (r'get (?P<room>#[a-zA-Z0-9-]+) feed display limit',
           self.get_feed_limit, 
          'Set number of messages per feed to display each time in room'), 
        )
        self.timer = task.LoopingCall(self.on_timer)

    def on_timer(self):
        self.output_feeds()

    def output_feeds(self, room=None):
        # If there are multiple feed subs get only those with
        # the oldest unprocessed messages.
        # TODO: we really need to restrict the model contents to one
        # feed per room
        if room:
            fsubs = FeedSub.objects.filter(\
                    target_irc__network = self.network,
                    target_irc__room = room.lower()).\
                    values('id', 'target_sub', 'target_irc__room').\
                    annotate(min_id = Min('feedprogress__processed_to'))

        else:
            fsubs = FeedSub.objects.filter(\
                    target_irc__network = self.network).\
                    values('id', 'target_sub', 'target_irc__room').\
                    annotate(min_id = Min('feedprogress__processed_to'))

        # For every feed subscription find its submissions
        for fsub_dict in fsubs:
            fsub = FeedSub.objects.get(pk=fsub_dict['id'])
            # Find all submissions that have not yet been displayed in IRC
            # rooms and output 'feed_limit' number of them from oldest to 
            # most recent subject to their start date

            fps = {} # dict of fp objects by subreddit name
            q_expr = None
            for subr in fsub.subreddits.all():
                try:
                    fp = FeedProgress.objects.get(feed = fsub, 
                            subreddit = subr)
                except FeedProgress.DoesNotExist:
                    #sub = Submission.objects.filter(subreddit=subr, created_at__gt = fsub.start_date ).first()
                    fp = FeedProgress(feed = fsub,
                            subreddit = subr,
                            processed_to = None)
                    # don't save this record yet

                # track fp by subreddit name in following dict
                fps[subr.name] = fp

                if fp.processed_to:
                    if q_expr:
                        q_expr |= Q(subreddit = subr) & Q(id__gt = fp.processed_to.id)
                    else:
                        q_expr = Q(subreddit = subr) & Q(id__gt = fp.processed_to.id)
                else:
                    if q_expr:
                        q_expr |= Q(subreddit = subr)
                    else:
                        q_expr = Q(subreddit = subr)
                # create our Q expression to filter out all
                # relevant subreddits
            feed_limit = get_room_option(self.network, 
                fsub.target_irc.room, "reddit-post-limit")
            if not feed_limit: 
                feed_limit = 1
            else:
                feed_limit = int(feed_limit)
            submissions = Submission.objects.filter(q_expr).order_by('created_at')[:feed_limit]
            for submission in submissions:
                fp = fps[submission.subreddit.name]
                room = fp.feed.target_irc.room
                created_at = submission.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
                title = submission.title
                body = submission.body[:80]
                url = submission.url
                msg = u"{} {} {} {}".format(created_at, title, body, url)
                self.say(room, msg) 
                fp.processed_to = submission

            # finally write the fp objects back to the database
            for fp in fps.itervalues():
                fp.save()


    def on_activate(self):
        """ When this plugin is activated for the network """
        self.timer.start(FEED_CHECK_TIME, now=False)
        logger.info("Feed check timer started")
        return (True, None)

    def on_deactivate(self):
        """ When this plugin is deactivated for the network """
        self.timer.stop()
        logger.info("Feed check timer stopped")

    def privmsg(self, user, channel, message):
        # Capture any matching urls and keep it in buffer
        pass

    @irc_room_permission_required('room_admin')
    def set_feed_limit(self, regex, chan, nick, **kwargs):
        """ Set the number of feed messages per feed limit """
        room = regex.group('room')
        limit = regex.group('count')
        set_room_option(self.network, room, "reddit-post-limit", limit)
        self.say(chan,"Reddit post limit set successfully set")
            
    def get_feed_limit(self, regex, chan, nick, **kwargs):
        """ Get the number of feed messages per feed """
        room = regex.group('room')
        feed_limit = get_room_option(self.network, room, "reddit-post-limit")
        self.say(chan,"Message post limit per reddit feed is {} messages".format(feed_limit))

    @irc_room_permission_required('room_admin')
    def pull_feeds(self, regex, chan, nick, **kwargs):
        self.output_feeds(chan.lower())

    @irc_room_permission_required('room_admin')
    def reset_feeds(self, regex, chan, nick, **kwargs):
        room = chan.lower()
        FeedProgress.objects.filter(feed__target_irc__network=self.network,
              feed__target_irc__room=room).delete()
        self.say(chan, "Reddit feed for room {} now reset".format(room))

    @irc_room_permission_required('room_admin')
    def add_subreddit(self, regex, chan, nick, **kwargs):
        subreddit_name = regex.group("subreddit")
        r = praw.Reddit(user_agent=REDDIT_UA)
        try:
            sub = Subreddits.objects.get(display_name__iexact = subreddit_name)
        except Subreddits.DoesNotExist:
            try:
                subobj = r.get_subreddit(subreddit_name, fetch=True)
                sub = Subreddits(name = subobj.name,
                        display_name = subobj.display_name,
                        url = subobj.url)
                sub.save()

            except praw.errors.InvalidSubreddit as e:
                self.say(chan, "subreddit does not exist")
                return

        username = self.get_auth().get_username(nick)
        user = User.objects.get(username = username)

        room_perm = RoomPermissions.objects.get(\
                network = self.network,
                room__iexact = chan)
        try:
            fsub = FeedSub.objects.get(target_irc = room_perm)
        except FeedSub.DoesNotExist:
            fsub = FeedSub(user = user,
                frequency = 60,
                target_irc = room_perm,
                post_limit = 3,
                # TODO: Make start_date a passed parameter
                start_date = timezone.make_aware(datetime.utcnow()-timedelta(days=7)),
                active = True)

            fsub.save()

        # The add method seems to be idempotent, ie a set, not a multiset
        # http://stackoverflow.com/questions/1417825/adding-the-same-object-twice-to-a-manytomanyfield
        fsub.subreddits.add(sub)
        self.say(chan, "successfully added subreddit")

    @login_required()
    def list_subreddits(self, regex, chan, nick, **kwargs):
        feedsubs = FeedSub.objects.filter(target_irc__network=self.network,
                target_irc__room = chan.lower(), active=True)
        if feedsubs:
            for feed in feedsubs:
                subs = [] # subreddits
                for subreddit in feed.subreddits.all():
                    subs.append(subreddit.display_name)
                subs_as_str = ",".join(subs)
                self.say(chan, "{} {}".format(feed.id, subs_as_str))
            self.say(chan, "End of reddit feeds lists")
        else:
            self.say(chan, "No reddit feeds found for this room")


    @irc_room_permission_required('room_admin')
    def remove_subreddit(self, regex, chan, nick, **kwargs):
        id = regex.group('id')
        username = self.get_auth().get_username(nick)
        user = User.objects.get(username = username)
        try:
            feed = FeedSub.objects.get(pk = id)
            feed.delete()
            self.say(chan, "Feed deleted successfully")
        except FeedSub.DoesNotExist:
            self.say(chan, "No feed {} exists for this room".format(id))


    def _get_one_feed(self, feed):
        results = []
        post_limit = feed.post_limit
        for subr in feed.subreddits.all():
            feed_prog, _ = FeedProgress.objects.get_or_create(feed = feed, subreddit = subr)
            if feed_prog.processed_to: 
                subs = Submission.objects.filter(subreddit=subr, pk__gt = feed_prog.processed_to.id)[:post_limit]
            else:
                subs = Submission.objects.filter(subreddit=subr, created_at__lt = feed.start_date)[:post_limit]
            cnt = feed_prog.processed
            for sub in subs:
                results.append(sub)
                cnt += 1
            feed_prog.processed = cnt
            if subs:
                feed_prog.processed_to = sub
            feed_prog.save()
        return results

    @login_required()
    def get_feed(self, regex, chan, nick, **kwargs):
        id = regex.group('id')
        try:
            feedsub = FeedSub.objects.get(pk = id, target_irc__isnull = False)
            subs = self._get_one_feed(feedsub)
            for sub in subs:
                self.say(chan, "{} {} {} {}".format(sub.created_at.strftime('%b %-d, %Y %-I:%M %p UTC'),
                    sub.author,
                    sub.title,
                    sub.url))
        except FeedSub.DoesNotExist:
            self.say(chan, "No feed {} exists for this room".format(id))

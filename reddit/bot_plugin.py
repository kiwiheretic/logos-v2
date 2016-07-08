# test plugin
from __future__ import absolute_import
from twisted.internet import task
from bot.pluginDespatch import Plugin
import re
import datetime
import time
import pytz
import logging
from .models import FeedSub, FeedProgress, Submission
from bot.logos_decorators import login_required, irc_room_permission_required
from logos.roomlib import get_global_option, set_global_option, \
    get_room_option, set_room_option

from django.db.models import Q  # for OR queryset
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
         (r'add feed (?P<url>https?://\S+) (?P<duration>\S+)$', self.add_feed, "Add a feed to feed list"),
         (r'add feed (?P<url>https?://\S+)$', self.add_feed, "Add a feed to feed list"),
         (r'reset feeds$', self.reset_feeds, "Reset feeds for current room"),
         (r'list feeds$', self.list_feeds, "List all feeds"),
         (r'pull feeds$', self.pull_feeds, "List all feeds"),
         (r'delete feed (?P<id>\d+)$', self.delete_feed, "delete a feed"),
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
        #self.output_feeds()
        pass

    def output_feeds(self, room=None):
        if room:
            feedsubs = FeedSubscription.objects.filter(network = self.network, room = room.lower()) 
            exclude_recs = CacheViews.objects.filter(network = self.network,
                    room = room.lower()).values('id')
        else:
            feedsubs = FeedSubscription.objects.filter(network = self.network) 
            exclude_recs = CacheViews.objects.filter(network = self.network).values('id')

        for sub in feedsubs:
            feed_limit = get_room_option(self.network, sub.room, "feed-post-limit")
            if not feed_limit: 
                feed_limit = 1
            else:
                feed_limit = int(feed_limit)
            cache_recs = Cache.objects.filter(feed = sub.feed).exclude(cacheviews__id__in = exclude_recs).order_by('published')
            for rec in cache_recs[:feed_limit]:
                title = rec.title
                link = rec.link
                if rec.description:
                    descr = "-" + rec.description[:120]
                    if len(rec.description) >= 120:
                        descr += " ..."


                else:
                    descr = ""
                published = rec.published.strftime("%b %d %Y %H:%M UTC")
                msg = u"{}: {}{} {}".format(published, title, descr, link)
                self.say(sub.room, msg)
                cv = CacheViews(network = self.network, room = sub.room,
                        cache = rec)
                cv.save()


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
        set_room_option(self.network, room, "feed-post-limit", limit)
        self.say(chan,"Feed post limit set successfully set")
            
    def get_feed_limit(self, regex, chan, nick, **kwargs):
        """ Get the number of feed messages per feed """
        room = regex.group('room')
        feed_limit = get_room_option(self.network, room, "feed-post-limit")
        self.say(chan,"Message post limit per feed is {} messages".format(feed_limit))

    @login_required()
    def pull_feeds(self, regex, chan, nick, **kwargs):
        self.output_feeds(chan.lower())

    @irc_room_permission_required('room_admin')
    def reset_feeds(self, regex, chan, nick, **kwargs):
        room = chan.lower()
        CacheViews.objects.filter(network=self.network,
              room=room).delete()
        self.say(chan, "Cache for room {} now reset".format(room))

    @irc_room_permission_required('room_admin')
    def add_feed(self, regex, chan, nick, **kwargs):
        username = self.get_auth().get_username(nick)
        user = User.objects.get(username = username)

        try:
            url = regex.group('url')
            r = requests.get(url)
            if r.status_code == 200:
                d = feedparser.parse(r.text)
                if d['entries']:
                    feed, _ = Feed.objects.get_or_create(feedurl = url)
                    feedsub = FeedSubscription(network = self.network,
                            room = chan.lower(),
                            user_added = user,
                            feed = feed,
                            periodic = "1h")
                    feedsub.save()
                    self.say(chan, 'Feed added successfully')
                else:
                    self.say(chan, 'Your url was not a valid feed')
            else:
                self.say(chan, "error {}".format(r.status_code))

        except requests.exceptions.ConnectionError:
            self.say(chan, "Unable to add feed {}, check url".format(url))

    @login_required()
    def list_feeds(self, regex, chan, nick, **kwargs):
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
    def delete_feed(self, regex, chan, nick, **kwargs):
        id = regex.group('id')
        try:
            feed = FeedSubscription.objects.get(network=self.network, room=chan.lower(), pk = id)
            feed.delete()
            self.say(chan, "Feed deleted successfully")
        except Feed.DoesNotExist:
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
                self.say(chan, "{} {} {} {}".format(sub.created_at,
                    sub.author,
                    sub.title,
                    sub.url))
        except FeedSub.DoesNotExist:
            self.say(chan, "No feed {} exists for this room".format(id))

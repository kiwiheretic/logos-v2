# test plugin
from __future__ import absolute_import
from bot.pluginDespatch import Plugin
import re
import datetime
import logging
from .models import Feed
import requests
import feedparser
from bot.logos_decorators import login_required

from django.contrib.auth.models import User
from django.conf import settings
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class FeedPlugin(Plugin):
    plugin = ("feed", "Atom+RSS Module")
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        
        self.commands = (\
         (r'add feed (?P<url>https?://\S+) (?P<duration>\S+)$', self.add_feed, "Add a feed to feed list"),
         (r'add feed (?P<url>https?://\S+)$', self.add_feed, "Add a feed to feed list"),
         (r'list feeds$', self.list_feeds, "List all feeds"),
         (r'delete feed (?P<id>\d+)$', self.delete_feed, "delete a feed"),
         (r'get feed (?P<id>\d+)$', self.get_feed, "get a feed"),
        )
    
    def privmsg(self, user, channel, message):
        # Capture any matching urls and keep it in buffer
        pass
            
    @login_required()
    def add_feed(self, regex, chan, nick, **kwargs):
        username = self.get_auth().get_username(nick)
        user = User.objects.get(username = username)

        try:
            url = regex.group('url')
            r = requests.get(url)
            if r.status_code == 200:
                d = feedparser.parse(r.text)
                if d['entries']:
                    feed = Feed(network = self.network,
                            room = chan.lower(),
                            user_added = user,
                            feedurl = url,
                            periodic = "1h")
                    feed.save()
                    self.say(chan, 'Feed added successfully')
                else:
                    self.say(chan, 'Your url was not a valid feed')
            else:
                self.say(chan, "error {}".format(r.status_code))

        except requests.exceptions.ConnectionError:
            self.say(chan, "Unable to add feed {}, check url".format(url))

    @login_required()
    def list_feeds(self, regex, chan, nick, **kwargs):
        feeds = Feed.objects.filter(network=self.network,
                room = chan.lower())
        if feeds:
            for feed in feeds:
                self.say(chan, "{} {}".format(feed.id, feed.feedurl))
            self.say(chan, "End of feeds lists")
        else:
            self.say(chan, "No feeds found for this room")


    @login_required()
    def delete_feed(self, regex, chan, nick, **kwargs):
        id = regex.group('id')
        try:
            feed = Feed.objects.get(network=self.network, room=chan.lower(), pk = id)
            feed.delete()
            self.say(chan, "Feed deleted successfully")
        except Feed.DoesNotExist:
            self.say(chan, "No feed {} exists for this room".format(id))



    @login_required()
    def get_feed(self, regex, chan, nick, **kwargs):
        id = regex.group('id')
        try:
            feed = Feed.objects.get(network=self.network, room=chan.lower(), pk = id)

            try:
                r = requests.get(feed.feedurl)
                if r.status_code == 200:
                    d = feedparser.parse(r.text)
                    title = d['feed']['title']
                    self.say(chan, u"Feed get {} successfully".format(title))
                    for entry in d.entries:
                        title = entry.title
                        link = entry.link
                        published = entry.published
                        self.say(chan, u"{}: {} {}".format(published, title, link))
                else:
                    self.say(chan, "Feed get error code {}".format(r.error_code))
            except requests.exceptions.ConnectionError:
                self.say(chan, "Unable to add feed {}, check url".format(url))
        except Feed.DoesNotExist:
            self.say(chan, "No feed {} exists for this room".format(id))

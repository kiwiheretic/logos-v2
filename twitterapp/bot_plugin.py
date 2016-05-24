# Twitter News Feed Plugin
from twisted.internet import task
from bot.pluginDespatch import Plugin
import re
import os
import twitter
import json
import HTMLParser

from datetime import timedelta, datetime
from dateutil import parser
import pytz
from models import TwitterStatuses, ReportedTweets, TwitterFollows
import logging
from logos.settings import LOGGING
from logos import utils 
from logos.roomlib import get_global_option, set_global_option, \
    get_room_option, set_room_option
    
from bot.logos_decorators import irc_network_permission_required, \
    irc_room_permission_required
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)


# If using this file as a starting point for your plugin
# then remember to change the class name 'MyBotPlugin' to
# something more meaningful.
class TwitterPlugin(Plugin):

    plugin = ('twitter', 'Twitter News Feed')
    
    def __init__(self, *args, **kwargs):
        super(TwitterPlugin, self).__init__(*args, **kwargs)
        self.commands = (\
                         (r'list\s+follows\s+(?P<room>#\S+)$',
                          self.list_follows, 'list all follows for room'),
                         (r'add\s+follow\s+(?P<room>#\S+)\s+(?P<follow>@\S+)', 
                          self.add_follow, 
                          'Add screen name to follow'),
                         (r'remove\s+follow\s+(?P<room>#\S+)\s+(?P<follow>@\S+)', 
                          self.remove_follow, 
                          'Remove screen name to follow'),                          
                         (r'set\s+(?P<room>#\S+)\s+twitter\s+display\s+limit\s+(?P<count>\d+)',
                           self.set_room_limit, 
                          'Set number of tweets to display each time in room'), 
                         (r'reset tweets (?P<room>#\S+)', self.reset, 
                          'Reset reported tweets'),
                         (r'set check time (\d+)', self.set_check_time, 
                          'set the twitter check time'),
                         (r'pull tweets',self.pull_tweet, "Pull some tweets without waiting for timer"),
                         
                         )
        

        self.timer = task.LoopingCall(self.on_timer)
        self.h = HTMLParser.HTMLParser()


       
    def on_activate(self):
        """ When this plugin is activated for the network """
        
        check_time = get_global_option("twitter-check-time")
        if check_time:
            check_time = int(check_time)
        else:
            check_time = 30
        logger.info("Twitter check timer is every {} seconds".format(check_time))
        self.timer.start(check_time, now=False)
        return (True, None)

    def on_deactivate(self):
        """ When this plugin is deactivated for the network """
        self.timer.stop()
        logger.info("Twitter check timer stopped")
        
    def privmsg(self, user, channel, message):
        pass
        
    @irc_network_permission_required('bot_admin')
    def set_check_time(self, regex, chan, nick, **kwargs):
        check_time = regex.group(1)
        set_global_option("twitter-check-time", check_time)
        self.timer.stop()
        self.timer.start(int(check_time), now=False)
        self.say(chan,"Twitter check time successfully set")
        
    @irc_room_permission_required('twitter_op')
    def set_room_limit(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        limit = regex.group('count')
        set_room_option(self.network, room, "twitter-post-limit", limit)
        self.say(chan,"Twitter post limit set successfully set")
    
    @irc_room_permission_required('twitter_op')
    def list_follows(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        self.say(chan, "List of twitter follows for room "+room)
        follows = TwitterFollows.objects.filter(network=self.network,
                                         room=room.lower())
        for follow in follows:
            self.say(chan, follow.screen_name)
        self.say(chan, "== End of List==")

    @irc_room_permission_required('twitter_op')
    def add_follow(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        follow = regex.group('follow')
        if TwitterFollows.objects.filter(network=self.network,
                                         room=room.lower(),
                                         screen_name__iexact=follow).exists():
            self.say(chan,"That follow already exists for this room")
        else:
            twit_follow = TwitterFollows()
            twit_follow.network = self.network
            twit_follow.room = room.lower()
            twit_follow.screen_name = follow
            twit_follow.save()
            self.say(chan,"Twitter follow added successfully")
    
    @irc_room_permission_required('twitter_op')
    def remove_follow(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        follow = regex.group('follow')
        try:
            twitterer = TwitterFollows.objects.get(network=self.network,
                                         room=room.lower(),
                                         screen_name__iexact=follow)
        except TwitterFollows.DoesNotExist:
            self.say(chan,"That follow doesn't exist for this room")
        else:
            twitterer.delete()
            self.say(chan,"Twitter follow removed successfully")
        
    @irc_room_permission_required('twitter_op')
    def reset(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        ReportedTweets.objects.filter(network=self.network,
                                      room=room).delete()
        self.say(chan,"Tweets for room {} now reset".format(room))
    
    def pull_tweet(self, regex, chan, nick, **kwargs):
        self.say(chan, "Manually requesting tweet")
        self._process_tweets(channel=chan)
        
        
    def on_timer(self):
        dt = datetime.now(pytz.utc)
        logger.debug("on_timer {}".format(str(dt)))
        self._process_tweets()
            
    def _process_tweets(self, channel=None):
        
        responses = []

        now = datetime.now(pytz.utc)
        n_days_ago = now - timedelta(days=365)

        statuses = TwitterStatuses.objects.\
            filter(created_at__gt = n_days_ago).\
                order_by('created_at')

        if channel:
            rooms = [ channel ]
        else:
            rooms = self.get_rooms()
        for room in rooms:
            if not self.is_plugin_enabled(room): continue

            limit = get_room_option(self.network, room, "twitter-post-limit")
            if limit:
                limit = int(limit)
            else:
                limit = 2
                
            count = 0
            for status in statuses:
                if status.reportedtweets_set.\
                    filter(network=self.network.lower(),
                           room=room.lower()).exists():
                    continue
                if not TwitterFollows.objects.filter(network=self.network.lower(),\
                room=room.lower(),\
                screen_name__iexact = "@"+status.screen_name).exists():
                    continue
                created_at = status.created_at.strftime("%d-%b-%Y %H:%M")         
                chan_text = "@{} {} -- {}".format(status.screen_name, 
                    created_at,
                    status.text.encode("ascii", "replace_spc"))

                responses.append((room, chan_text))
                reported_twt = ReportedTweets()
                reported_twt.tweet = status
                reported_twt.network = self.network.lower()
                reported_twt.room = room.lower()
                reported_twt.save()
                
                count += 1
                
                if count >= limit: break
            for room, msg in responses:
                if not self.is_plugin_enabled(room): continue
                msg = re.sub(r"\n|\r", "", msg)
                msg = self.h.unescape(msg)

                self.say(room, msg)
            if not responses and channel: # manual pull
                self.say(channel, "=== No Tweets Found ===")
            

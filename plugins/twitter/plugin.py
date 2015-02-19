# Twitter News Feed Plugin
from twisted.internet import task
from bot.pluginDespatch import Plugin
import re
import os
import twitter
import json

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
        Plugin.__init__(self, *args, **kwargs)
        self.commands = (\
                         (r'list\s+follows\s+(?P<room>#[a-zA-z0-9-]+)$',
                          self.list_follows, 'list all follows for room'),
                         (r'add\s+follow\s+(?P<room>#[a-zA-z0-9-]+)\s+(?P<follow>@[a-zA-Z_]+)', 
                          self.add_follow, 
                          'Add screen name to follow'),
                         (r'remove\s+follow\s+(?P<room>#[a-zA-z0-9-]+)\s+(?P<follow>@[a-zA-Z_]+)', 
                          self.remove_follow, 
                          'Add screen name to follow'),                          
                         (r'set\s+(?P<room>#[a-zA-z0-9-]+)\s+twitter\s+display\s+limit\s+(?P<count>)',
                           self.set_room_limit, 
                          'Set number of tweets to display each time in room'), 
                         (r'reset\s+(?P<room>#[a-zA-z0-9-]+)', self.reset, 
                          'Reset reported tweets'),
                         (r'set check time (\d+)', self.set_check_time, 
                          'set the twitter check time'),
                         
                         )
        pth = os.path.dirname(__file__)
        f = open(os.path.join(pth,"secrets.json"), "r")
        json_secrets = json.load(f)
        
        self.consumer_key = json_secrets['consumer_key']
        self.consumer_secret = json_secrets['consumer_secret']
        self.access_token = json_secrets['access_token']
        self.token_secret = json_secrets['token_secret']
        
        self.api = twitter.Api(consumer_key=self.consumer_key,
                      consumer_secret=self.consumer_secret,
                      access_token_key=self.access_token,
                      access_token_secret=self.token_secret)

        self.timer = task.LoopingCall(self.on_timer)
        

    def signedOn(self):
        check_time = get_global_option("twitter-check-time")
        if check_time:
            check_time = int(check_time)
        else:
            check_time = 30
        logger.info("Twitter check timer is every {} seconds".format(check_time))
        self.timer.start(check_time, now=False)

       
    def privmsg(self, user, channel, message):
        pass
        
    @irc_network_permission_required('net_admin')
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
    
    def list_follows(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        self.notice(nick, "List of twitter follows for room "+room)
        follows = TwitterFollows.objects.filter(network=self.network,
                                         room=room.lower())
        for follow in follows:
            self.notice(nick, follow.screen_name)
        self.notice(nick, "== End of List==")

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
    
    def on_timer(self):
        dt = datetime.now(pytz.utc)
        logger.info("on_timer {}".format(str(dt)))
        follows = TwitterFollows.objects.filter(network=self.network).\
            values('screen_name').distinct()
                                      
        get_tweets_from = [x['screen_name'] for x in follows]
        for tweeter in get_tweets_from:
            last_tweet = TwitterStatuses.objects.\
                filter(screen_name__iexact=tweeter[1:]).order_by('twitter_id').last()
            if last_tweet:
                since_id = long(last_tweet.twitter_id)
#                logger.info("Since ID = " + str(since_id))
                statuses = self.api.GetUserTimeline(screen_name=tweeter,
                                                    since_id = since_id)
            else:
                statuses = self.api.GetUserTimeline(screen_name=tweeter)
            
            for status in statuses:
                if TwitterStatuses.objects.filter(twitter_id=status.id).exists():
                    logger.info("Twitter status {} already exists".format(status.id))
                else:
                    ts = TwitterStatuses()
                    ts.twitter_id = status.id
                    ts.screen_name = status.user.screen_name
                    try:
                        ts.url = status.urls[0].url
                    except IndexError:
                        ts.url = None
                    ts.text = status.text
                    ts.created_at = parser.parse(status.created_at)
                    ts.save()        
        

        now = datetime.now(pytz.utc)
        n_days_ago = now - timedelta(days=14)

        statuses = TwitterStatuses.objects.\
            filter(created_at__gt = n_days_ago).\
                order_by('created_at')

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
                        
                if count==0:
                    self.say(room, "Your Christian Twitter Feed :)")
                    
                chan_text = "@{} -- {}".format(status.screen_name,
                                           status.text.encode("ascii", "replace_spc"))
                self.say(room, chan_text)
                reported_twt = ReportedTweets()
                reported_twt.tweet = status
                reported_twt.network = self.network.lower()
                reported_twt.room = room.lower()
                reported_twt.save()
                
                count += 1
                
                if count >= limit: break
        
        




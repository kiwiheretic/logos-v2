# Twitter News Feed Plugin
from twisted.internet import task
from bot.pluginDespatch import Plugin
import re
import twitter

from datetime import timedelta, datetime
from dateutil import parser
import pytz
from models import TwitterStatuses, ReportedTweets
import logging
from logos.settings import LOGGING
from logos import utils 
from logos.roomlib import get_global_option, set_global_option
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

# If using this file as a starting point for your plugin
# then remember to change the class name 'MyBotPlugin' to
# something more meaningful.
class TwitterPlugin(Plugin):
    # Uncomment the line below to load this plugin.  Also if
    # you are using this as a starting point for your own plugin
    # remember to change 'sample' to be a unique identifier for your plugin,
    # and 'My Bot Plugin' to a short description for your plugin.
    plugin = ('twitter', 'Twitter News Feed')
    
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.commands = (\
                         (r'reset\s+(?P<room>#[a-zA-z0-9-]+)', self.reset, 'Reset reported tweets'),
                         (r'set check time (\d+)', self.set_check_time, 
                          'set the twitter check time'),
                         
                         )
        self.consumer_key = 'JHzzZAYjH1zgyU8OoG212WpVV'
        self.consumer_secret = 'TqsPhyeMeO6WP891pN3gHvbvmtBcngx73wTBnlzyJoIJrHgBTJ'
        self.access_token = '111150874-u6taQyCTOwsxj00OfcwXXcg5UyZbEoHgyifk9rzI'
        self.token_secret = 'uD2vcl7Dw4atWAFZQeBWjbu468Z13Vu7pvSxIPnXpMmtA'
        
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
    
    def set_check_time(self, regex, chan, nick, **kwargs):
        check_time = regex.group(1)
        set_global_option("twitter-check-time", check_time)
        self.timer.stop()
        self.timer.start(int(check_time), now=False)
        self.say(chan,"Twitter check time successfully set")
        
    def reset(self, regex, chan, nick, **kwargs):
        room = regex.group('room')
        ReportedTweets.objects.filter(network=self.network,
                                      room=room).delete()
        self.say(chan,"Tweets for room {} now reset".format(room))

    
    def on_timer(self):
        logger.info("on_timer")
        get_tweets_from = ('@pastorangelaw','@captive_setfree' )
        for tweeter in get_tweets_from:
            last_tweet = TwitterStatuses.objects.\
                filter(screen_name=tweeter[1:]).order_by('twitter_id').last()
            if last_tweet:
                since_id = last_tweet.twitter_id
                statuses = self.api.GetUserTimeline(screen_name=tweeter,
                                                    since_id = since_id)
            else:
                statuses = self.api.GetUserTimeline(screen_name=tweeter)
            
            for status in statuses:
                ts = TwitterStatuses()
                ts.twitter_id = status.id
                ts.screen_name = status.user.screen_name
                ts.url = status.urls[0].url
                ts.text = status.text
                ts.created_at = parser.parse(status.created_at)
                ts.save()        
        

        now = datetime.now(pytz.utc)
        n_days_ago = now - timedelta(days=14)

        statuses = TwitterStatuses.objects.\
            filter(created_at__gt = n_days_ago).\
                order_by('created_at')
        
        limit = 2
        rooms = self.get_rooms()
        for room in rooms:
            if not self.is_plugin_enabled(room): continue
            count = 0
            for status in statuses:
                if status.reportedtweets_set.\
                    filter(network=self.network.lower(),
                           room=room.lower()).exists():
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
        
        




from django.core.management.base import BaseCommand, CommandError
from twitterapp.models import TwitterFollows, TwitterStatuses 

from dateutil import parser as dateparser
from logos.roomlib import get_global_option
import twitter
import sys

class Command(BaseCommand):
    help = 'Pull tweets from twitter'

    def add_arguments(self, parser):
        parser.add_argument('subcommand', nargs='?')
        

    def handle(self, *args, **options):
        subcommand = options['subcommand']
        if subcommand:
            self.stdout.write('Nothing done')
        else:

            self.get_tweets()
            self.stdout.write('Successfully finished pulling tweets from Twitter')

    def get_tweets(self):
        consumer_key = get_global_option('twitter-consumer-key')
        consumer_secret = get_global_option('twitter-consumer-secret')
        access_token = get_global_option('twitter-access-token')
        token_secret = get_global_option('twitter-token-secret')
        api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=access_token,
                      access_token_secret=token_secret)        

        follows = TwitterFollows.objects.all().\
            values('screen_name').distinct()
                                      
        get_tweets_from = [x['screen_name'] for x in follows]
        for tweeter in get_tweets_from:
            try:
                last_tweet = TwitterStatuses.objects.\
                    filter(screen_name__iexact=tweeter[1:]).order_by('twitter_id').last()
                if last_tweet:
                    since_id = long(last_tweet.twitter_id)
                    statuses = api.GetUserTimeline(screen_name=tweeter,
                                                        since_id = since_id)
                else:
                    statuses = api.GetUserTimeline(screen_name=tweeter)
                
                sys.stdout.write("Number of new tweets for {} = {}\n".format(tweeter, len(statuses)))
                for status in statuses:
                    if TwitterStatuses.objects.filter(twitter_id=status.id).exists():
                        sys.stdout.write("Twitter status {} already exists".format(status.id))
                    else:
                        ts = TwitterStatuses()
                        ts.twitter_id = status.id
                        ts.screen_name = status.user.screen_name
                        try:
                            ts.url = status.urls[0].url
                        except IndexError:
                            ts.url = None
                        ts.text = status.text
                        ts.created_at = dateparser.parse(status.created_at)
                        ts.save()        
            
            except twitter.error.TwitterError:
                sys.stdout.write("An error occurred fetching tweets")

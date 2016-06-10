from django.core.management.base import BaseCommand, CommandError

#from dateutil import parser as dateparser
import sys
import requests
import pytz

from ...models import Feed, Cache
import feedparser
import datetime
import time

from django.conf import settings
import logging

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class Command(BaseCommand):
    help = 'Pull RSS and Atom feeds'

    def add_arguments(self, parser):
        parser.add_argument('subcommand', nargs='?')
        

    def handle(self, *args, **options):
        subcommand = options['subcommand']
        if subcommand:
            self.stdout.write('Nothing done')
        else:

            self.get_feeds()
            self.stdout.write('Successfully finished pulling RSS feeds')

    def get_feeds(self):
        feedsubs = Feed.objects.filter(active=True)
        for feed in feedsubs:
            url = feed.feedurl
            try:
                logger.info('Feed requesting url {}'.format(url))
                r = requests.get(url)
                if r.status_code == 200:
                    d = feedparser.parse(r.text)
                    for entry in d['entries']:
                        if not Cache.objects.filter(guid = entry.id).exists():

                            # assume published date is in UTC timezone and 
                            # convert to datetime object
                            published_date = pytz.utc.localize(datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed)))

                            if hasattr(entry,'description'):
                                description = entry.description
                            else:
                                description = None

                            cache = Cache(feed = feed,
                                    guid = entry.id,
                                    link = entry.link,
                                    title = entry.title,
                                    description = description,
                                    published = published_date)
                            cache.save()
            except requests.exceptions.ConnectionError:
                pass

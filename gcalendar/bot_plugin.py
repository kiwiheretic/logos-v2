# test plugin
from bot.pluginDespatch import Plugin
import re
import datetime
import dateutil
import logging
import httplib2

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from oauth2client.django_orm import Storage

from django.conf import settings
from django.contrib.auth.models import User

from .models import SiteModel, FlowModel, CredentialsModel

from bot.logos_decorators import login_required

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class GoogleCalendarPlugin(Plugin):
    plugin = ("gcal", "Google Calendar Plugin")
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)

        self.commands = (\
         (r'events', self.list, "display a list of google calendar events"),
#         (r'urls\s+(?P<room>#[a-zA-z0-9-]+)$', self.urls_display, "display a list of captured urls"),
        )
        self.userlist = {}

    def onSignal_login(self, source, data):
        nick = data['nick']
        username = self.get_auth().get_username(nick)
        user = User.objects.get(username=username)

        storage = Storage(CredentialsModel, 'id', user, 'credential')
        self.userlist[username] = {'storage':storage}
    
    @login_required()
    def list(self, regex, chan, nick, **kwargs):
        username = self.get_auth().get_username(nick)
        storage = self.userlist[username]['storage']

        credentials = storage.get()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        self.notice(nick, 'Getting your next 10 (or fewer) upcoming Google Calendar events')
        eventsResult = service.events().list(
            calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])
        for event in events:
            if 'date' in event['start']:
                start_date = event['start']['date']
            elif 'dateTime' in event['start']:
                start_date = event['start']['dateTime']
            else:
                start_date = None  # unhandled error
            dt = dateutil.parser.parse(start_date)
            estr = "{} {}".format(str(dt), event['summary'])
            self.notice(nick, estr)


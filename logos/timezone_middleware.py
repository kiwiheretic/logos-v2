import pytz

from django.utils import timezone
from logos.roomlib import get_user_option

class TimezoneMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            tzname = get_user_option(request.user, 'timezone')
        else:
            tzname = None
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()

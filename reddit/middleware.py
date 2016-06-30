from __future__ import absolute_import
from django.conf import settings
from .models import RedditCredentials

import logging
from django.conf import settings 
logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class RedditMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and 'reddit_username' not in request.session:
            try:
                cred = RedditCredentials.objects.get(user = request.user)
                request.session['reddit_username'] = cred.reddit_username
            except RedditCredentials.DoesNotExist:
                pass


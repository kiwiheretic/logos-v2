from __future__ import absolute_import
from django.shortcuts import render, redirect
from django.http import Http404
from logos.roomlib import get_global_option, set_global_option
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

import praw
import pickle
import datetime
from .forms import SiteSetupForm
from .models import RedditCredentials, MySubreddits

REDDIT_BOT_DESCRIPTION = 'Reddit plugin for IRC Logos u/kiwiheretic ver 0.1'
# Create your views here.

@login_required
def site_setup(request):
    if request.method == "POST":
        form = SiteSetupForm(request.POST)
        if form.is_valid():
            consumer_key = form.cleaned_data['consumer_key']
            consumer_secret = form.cleaned_data['consumer_secret']
            set_global_option('reddit-consumer-key', consumer_key)
            set_global_option('reddit-consumer-secret', consumer_secret)
            messages.add_message(request, messages.INFO, 'API key saved successfully')
    else:
        consumer_key = get_global_option('reddit-consumer-key')
        consumer_secret = get_global_option('reddit-consumer-secret')
        init = {'consumer_key':consumer_key, 'consumer_secret':consumer_secret}
        form = SiteSetupForm(initial=init)
    return render(request, 'reddit/site_setup.html', {'form':form})


@login_required
def user_setup(request):
    try:
        credentials = RedditCredentials.objects.get(user = request.user)
        print credentials.tokens()
        return render(request, 'reddit/tokens.html', {'credentials':credentials})
    except RedditCredentials.DoesNotExist:
        return render(request, 'reddit/user_setup.html')

def get_r(request):
    """ Prepare the reddit variable handle 'r' for use.
    Called mainly as a helper function by view methods proper. """
    consumer_key = get_global_option('reddit-consumer-key')
    consumer_secret = get_global_option('reddit-consumer-secret')
    r = praw.Reddit(REDDIT_BOT_DESCRIPTION)

    # Set authorised app via https://www.reddit.com/prefs/apps
    redirect_url = request.scheme + "://" + request.META['HTTP_HOST'] + reverse('reddit.views.oauth_callback')

    r.set_oauth_app_info(client_id=consumer_key,
                         client_secret=consumer_secret,
                         redirect_uri=redirect_url)
    return r

@login_required
def oauth_callback(request):
    if 'error' in request.GET:
        error = request.GET['error']
        logger.info('reddit oauth callback error : {} '.format(error))
        messages.error(request, 'There was a problem with your Reddit permissions grant. Error: {} '.format(error))
        return redirect(reverse('reddit.views.user_setup'))
    r = get_r(request)
    code = request.GET['code']
    try:
        access_information = r.get_access_information(code)
        print access_information
        access_data = pickle.dumps(access_information)
        credentials, _ = RedditCredentials.objects.get_or_create(user = request.user)
        credentials.token_data = access_data
        credentials.created_at = datetime.datetime.now()
        credentials.save()
        messages.info(request, "Reddit credentials saved successfully")


    except praw.errors.OAuthInvalidGrant:
        logger.info("Invalid OAuth Grant to {} ".format(request.user.username))
        messages.error(request, 'There was a problem with your Reddit permissions grant.')
    return redirect(reverse('reddit.views.user_setup'))

@login_required
def authorise(request):
    r = get_r(request)
    url = r.get_authorize_url('logosRedditKey', 'identity read mysubreddits submit', True)
    return redirect(url)

@login_required
def discard_tokens(request):
    try:
        RedditCredentials.objects.get(user = request.user).delete()
        messages.success(request, 'Reddit tokens successfully discarded')
        return redirect(reverse('reddit.views.user_setup'))
    except RedditCredentials.DoesNotExist:
        raise Http404("Reddit credentials for user not found")

@login_required
def my_subreddits(request):
    try:
        mysubs = MySubreddits.objects.get(user = request.user)
    except MySubreddits.DoesNotExist:
        mysubs = None
    return render(request, 'reddit/my_subreddits.html', {'mysubs':mysubs})

from __future__ import absolute_import
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.utils import timezone
from logos.roomlib import get_global_option, set_global_option
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

import praw
import pickle
import datetime
import socket
from .forms import SiteSetupForm, RedditSubmitForm
from .models import RedditCredentials, MySubreddits, Submission, PendingSubmissions, Subreddits, FeedSub

REDDIT_BOT_DESCRIPTION = 'Heretical by /u/kiwiheretic ver 0.1'
UDP_IP = "127.0.0.1"
UDP_PORT = 5011
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
    redirect_url = request.scheme + "://" + request.META['HTTP_HOST'] + reverse('reddit:oauth_callback')

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
        r.set_access_credentials(**access_information)
        authenticated_user = r.get_me()
        credentials, _ = RedditCredentials.objects.get_or_create(user = request.user)
        credentials.token_data = access_data
        credentials.reddit_username = authenticated_user.name
        credentials.created_at = datetime.datetime.now()
        credentials.save()
        messages.info(request, "Reddit credentials saved successfully")


    except praw.errors.OAuthInvalidGrant:
        logger.info("Invalid OAuth Grant to {} ".format(request.user.username))
        messages.error(request, 'There was a problem with your Reddit permissions grant.')
    return redirect(reverse('reddit:user_setup'))

@login_required
def authorise(request):
    r = get_r(request)
    url = r.get_authorize_url('logosRedditKey', 'identity read mysubreddits submit', True)
    return redirect(url)

@login_required
def discard_tokens(request):
    try:
        RedditCredentials.objects.get(user = request.user).delete()
        try:
            del request.session['reddit_username']
        except KeyError:
            pass
        messages.success(request, 'Reddit tokens successfully discarded')
        return redirect(reverse('reddit:user_setup'))
    except RedditCredentials.DoesNotExist:
        raise Http404("Reddit credentials for user not found")

@login_required
def my_subreddits(request):
    try:
        mysubs = MySubreddits.objects.get(user = request.user)
    except MySubreddits.DoesNotExist:
        mysubs = None
        
    feeds = FeedSub.objects.filter(user=request.user)
    return render(request, 'reddit/my_subreddits.html', {'mysubs':mysubs, 'feeds':feeds})

@login_required
def list_posts(request, subreddit):
    posts = Submission.objects.filter(subreddit__display_name = subreddit).order_by('-created_at')
    paginator = Paginator(posts, 10) # Show 10 comments per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)
    posts_list = ", ".join([str(p.id) for p in posts.object_list])
    if posts_list:
        sock = socket.socket(socket.AF_INET, # Internet
            socket.SOCK_DGRAM) # UDP
        sock.sendto("commentise "+posts_list, (UDP_IP, UDP_PORT))
    return render(request, 'reddit/list_posts.html', {'subreddit':subreddit, 'posts':posts})


@login_required
def post_detail(request, post_id):
    sub = get_object_or_404(Submission, pk = post_id)
    comment_list = sub.comments_set.order_by('created_at')
    paginator = Paginator(comment_list, 10) # Show 10 comments per page

    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        comments = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        comments = paginator.page(paginator.num_pages)

    return render(request, 'reddit/post_detail.html', {"submission":sub, "comments": comments})


@login_required
def new_post(request):
    choices = []
    try:
        my_subreddits = MySubreddits.objects.get(user = request.user).subreddits.all()
        for mysub in my_subreddits:
            choices.append((mysub.id, mysub.display_name))
    except MySubreddits.DoesNotExist:
        pass
    if request.method == 'POST':
        form = RedditSubmitForm(request.POST, choices = choices)
        if form.is_valid():
            psub = PendingSubmissions()
            psub.user = request.user
            subr = Subreddits.objects.get(pk = int(form.cleaned_data['subreddit']))   
            psub.subreddit = subr
            psub.title = form.cleaned_data['title']
            psub.body = form.cleaned_data['body']
            psub.created_at = timezone.now()
            psub.save()
            messages.add_message(request, messages.INFO, 'Submission successfully saved for upload')
            return redirect(reverse('reddit:mysubreddits'))
    else:
        form = RedditSubmitForm(choices = choices)
    return render(request, 'reddit/new_post.html', {'form':form})

@login_required
def delete_feed(request, feed_id):
    feed = FeedSub.objects.get(pk = feed_id, user = request.user)
    feed.delete()
    return redirect(reverse('reddit:mysubreddits'))

    pass

@login_required
def pending_posts(request):
    posts = PendingSubmissions.objects.filter(user = request.user).order_by('created_at')
    paginator = Paginator(posts, 10) # Show 10 comments per page

    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects = paginator.page(paginator.num_pages)

    return render(request, 'reddit/pending_posts.html', {"posts":objects})

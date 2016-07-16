from __future__ import absolute_import
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from django.utils import timezone
from django.db.utils import IntegrityError

from logos.roomlib import get_global_option

import sys
import pytz
import praw

import datetime
from ...models import RedditCredentials, MySubreddits, Subreddits, Submission, Comments, PendingSubmissions, FeedSub, FeedProgress
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)

class Command(BaseCommand):
    help = 'Perform regular reddit database maintenance'

    def add_arguments(self, parser):
        parser.add_argument('subcommand', nargs='?')
        parser.add_argument('--port', type=int, action='store')
        

    def handle(self, *args, **options):
        subcommand = options['subcommand']
        if subcommand:
            self.stdout.write('Subcommand = '+subcommand)
        if options['port']:
            port = options['port']
        else:
            port = None

        self.reddit_maintenance(port, subcommand)
        self.stdout.write('Successfully finished reddit maintenance.')

    def reddit_maintenance(self, port, subcommand):
        if subcommand == "commentsonly":
            self.authenticate(port)
            self.get_comments()
        elif subcommand == "processfeeds":
            self.authenticate(port)
            self.process_feeds()
        elif subcommand == "fixusernames":
            self.authenticate(port)
            self.fix_reddit_usernames()
        elif subcommand == "submitonly":
            self.authenticate(port)
            self.post_pending()
        elif subcommand == None:
            self.authenticate(port)
            self.post_pending()
            self.my_subreddits()
            self.get_submissions()

    def authenticate(self, port):
        site = Site.objects.get(pk=settings.SITE_ID)
        self.r = praw.Reddit('Heretical v0.1 by /u/kiwiheretic '
                'https://github.com/kiwiheretic/logos-v2 for source')
        consumer_key = get_global_option('reddit-consumer-key')
        consumer_secret = get_global_option('reddit-consumer-secret')
        redirect_uri = 'http://' + site.domain
        if port:
            redirect_uri += ":"+str(port)
        redirect_uri += '/reddit/oauth-callback/'
        self.r.set_oauth_app_info(client_id=consumer_key,
                 client_secret=consumer_secret,
                 redirect_uri=redirect_uri)

    def post_pending(self):
        """ Post pending submissions to reddit """
        psubs = PendingSubmissions.objects.filter(uploaded_at__isnull=True).order_by('user')
        luser = None
        for psub in psubs:
            if luser == None or luser != psub.user:
                credentials = RedditCredentials.objects.get(user = psub.user).credentials()
                self.r.set_access_credentials(**credentials)
                authenticated_user = self.r.get_me()
                print "authenticated user = "+authenticated_user.name
                subreddit = psub.subreddit.display_name
                sig = "** submitted by logos bot: https://github.com/kiwiheretic/logos-v2"
                try:
                    submission = self.r.submit(subreddit, psub.title, 
                        text=psub.body + "  \n" + sig,
                        raise_captcha_exception = False)
                    print ("submitted submission successfully")
                    psub.uploaded_at=timezone.now()
                    psub.save()
                except praw.errors.RateLimitExceeded:
                    pass
            luser = psub.user
            #psub.submitted = True
            #psub.save()


    def fix_reddit_usernames(self):
        for redcred in RedditCredentials.objects.filter(reddit_username = None):
            credentials = redcred.credentials()
            self.r.set_access_credentials(**credentials)
            authenticated_user = self.r.get_me()
            redcred.reddit_username = authenticated_user.name
            print (authenticated_user.name)
            redcred.save()


    def _save_submission_to_db(self, subreddit, thing_paginator):
        cnt = 0
        sr = self.r.get_subreddit(subreddit.display_name)
        if thing_paginator:
            listing = sr.get_new(limit=None, params={'before':thing_paginator})
        else:
            listing = sr.get_new(limit=None)

        for sub in listing:
            # Don't save deleted posts (ie. author is blank)
            # https://www.reddit.com/r/redditdev/comments/1630jj/praw_is_returning_postauthorname_errors/c7s8zx9
            cnt += 1
            if not sub.author: continue

            cdate = datetime.datetime.fromtimestamp(
                            int(sub.created_utc)
                                )
            udate = timezone.make_aware(cdate, timezone = pytz.utc)
            try:
                post = Submission(name = sub.name,
                        created_at = udate,
                        subreddit = subreddit,
                        title = sub.title,
                        author = sub.author,
                        body = sub.selftext,
                        url = sub.url,
                        score = sub.score,
                        link_flair_text = sub.link_flair_text,
                        num_comments = sub.num_comments)
                post.save()
            except IntegrityError:
                if Submission.objects.filter(name = sub.name).exists():
                    print "{} already exists".format(sub.name)
                else:
                    print "Error: Could not insert {} {}".format(sub.name, sub.title)
                    import pdb; pdb.set_trace()
            else:
                print sub.name, udate, sub.num_comments, repr(sub.title)
        return cnt


    def get_submissions(self):
        for subr in Subreddits.objects.filter(active=True):
            # if a new subreddit has not yet any submissions
            # in database then we need to set cnt = 0 to
            # test for that also
            cnt = 0
            print subr.display_name
            # Need to check more than last sub because last sub may have been 
            # deleted and this silently fails with the current api
            # https://www.reddit.com/r/redditdev/comments/4rwmh3/get_new_returning_no_posts_but_browser_equivalent/
            last_subs = Submission.objects.filter(subreddit = subr).order_by('-created_at')[0:5]
            for idx, last_sub in enumerate(last_subs):
                if last_sub:
                    thing = last_sub.name
                else:
                    thing = None
                cnt = self._save_submission_to_db(subr, thing)
                if cnt > 0:
                    break
            # if backtracking thru the last things in the database in our
            # efforts to find a paginator then give up trying with the
            # paginator and just get what we can.  (In other words it seems like
            # a whole block of database records have been deleted from reddit).
            if cnt == 0:
                self._save_submission_to_db(subr, None)

    def my_subreddits(self):
        Subreddits.objects.all().update(active=False)
        for cred in RedditCredentials.objects.all():
            access = cred.credentials()
            self.r.set_access_credentials(**access)
            authenticated_user = self.r.get_me()
            print authenticated_user.name, authenticated_user.link_karma
            try:
                mysubs = MySubreddits.objects.get(user=cred.user)
                # remove all subreddit subscriptions
                # we will repopulate them afresh
                mysubs.subreddits.clear()
            except MySubreddits.DoesNotExist:
                pass

            for sub in self.r.get_my_subreddits():
                print sub.name, sub.display_name, sub.url
                obj, _ = Subreddits.objects.get_or_create(name = sub.name,
                        defaults = {'display_name':sub.display_name,
                            'url' : sub.url})
                # Mark any subreddits subscribed as active
                obj.active = True
                obj.save()
                mysub, _ = MySubreddits.objects.get_or_create(user = cred.user)
                mysub.subreddits.add(obj)

    def process_feeds(self):
        feeds = FeedSub.objects.filter(target_sub__isnull = False).order_by('user')
        user = None
        for feed in feeds:
            if feed.user != user:
                # authenticate user
                credentials = RedditCredentials.objects.get(user = feed.user).credentials()
                self.r.set_access_credentials(**credentials)
                # Now check subreddits for new posts we can poach
                for sub in feed.subreddits.all():
                    try:
                        fp = FeedProgress.objects.get(feed = feed, feed__user = feed.user)
                    except FeedProgress.DoesNotExist:
                        fp = FeedProgress( \
                                feed = feed,
                                subreddit = sub,
                                processed_to = None,
                                processed = 0)
                        fp.save()
                    self._process_subreddit_feeds(fp)
            user = feed.user

    def _process_subreddit_feeds(self, fp):
        post_limit = fp.feed.post_limit
        if fp.processed_to:
            subs = Submission.objects.filter(subreddit = fp.subreddit,
                    id__gt = fp.processed_to.id).order_by('id')
        else:
            start_date = fp.feed.start_date
            subs = Submission.objects.filter(subreddit = fp.subreddit,
                    created_at__gt = start_date).order_by('id')
        target_subreddit = fp.feed.target_sub.display_name
        sig = "** submitted by logos bot: https://github.com/kiwiheretic/logos-v2"

        for ii, sub in enumerate(subs):
            try:
                submission = self.r.submit(target_subreddit, sub.title, 
                    text=sub.body + "\n" + sig,
                    raise_captcha_exception = False)
                print ("submitted submission successfully")
            except praw.errors.RateLimitExceeded as e:
                print ('RateLimit Exception - ban time = {} seconds'.format(e.sleep_time))
                break
            fp.processed_to = sub
            fp.save()
            if ii > post_limit:
                break

    def _traverse_comments(self, submission, submission_obj, parent):
        if parent == None:
            comments = submission_obj.comments
        else:
            comments = parent.replies
        for comment in comments:
            if not hasattr(comment, 'author') or not comment.author: continue
            cdate = datetime.datetime.fromtimestamp(
                int(comment.created_utc)
                )
            udate = timezone.make_aware(cdate, timezone = pytz.utc)
            if parent:
                parent_name = parent.name
            else:
                parent_name = submission.name
            try:
                comm = Comments(name = comment.name,
                        submission = submission,
                        parent_thing = parent_name,
                        created_at = udate,
                        author = comment.author.name,
                        body = comment.body,
                        score = comment.score)
                comm.save()
                print comm.name
            except IntegrityError:
                pass

            self._traverse_comments(submission, submission_obj, comment)


    def get_comments(self):
        for sub in Submission.objects.all().order_by('-created_at'):
            subobj = self.r.get_info(thing_id = sub.name)
            print subobj.num_comments
            sub.num_comments = subobj.num_comments
            sub.save()
            subreddit_name = sub.subreddit.display_name
            comments = self.r.get_comments(subreddit_name, params={'context':0, 'depth':1})
            for comment in comments:
                try:
                    c = Comments(name = comment.name,
                            submission = sub,
                            parent_thing = sub.name,
                            created_at = timezone.now(),
                            author = comment.author,
                            body = comment.body,
                            score = comment.score)
                    c.save()
                except IntegrityError:
                    pass


            #self._traverse_comments(sub,subobj, None)




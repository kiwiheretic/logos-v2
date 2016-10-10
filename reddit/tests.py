from __future__ import absolute_import

from django.test import TestCase
import datetime
import re
from django.utils import timezone

# Import the plugin you wish to test
from .bot_plugin import RedditPlugin
from .models import Submission, Subreddits, FeedProgress, FeedSub

# Subclass your test class from LogosTestCase
from bot.testing.utils import LogosTestCase

class TestReddit(LogosTestCase):
    # set plugin_class to the actual class
    # of the plugin you wish to test
    plugin_class = RedditPlugin
    def setUp(self):
        self.fred = self.create_user('fred', "fred@noemail.com", "password1")

    def testRedditWithRoom(self):
        self.assign_room_permission('fred', self.room, 'room_admin')
        self.set_nick("fred")
        self.login("password1")

        output = self.plugin.send_command("add subreddit /r/askphysics")
        self.assertIn('successfully added subreddit', output)

        # Test subreddit subscription creation
        output = self.plugin.send_command("add subreddit /r/gobbledegookzzz")
        self.assertIn('subreddit does not exist', output)
        
        output = self.plugin.send_command("list subreddits")
        self.assertIn('AskPhysics', output)
        sub_id = re.search(r"(\d+) AskPhysics", output).group(1)

        # create some test data
        subreddit = Subreddits.objects.get(display_name__iexact = "askphysics")
        post = Submission(name = "t5_fake1",
                created_at = timezone.make_aware(datetime.datetime.utcnow()),
                subreddit = subreddit,
                title = "first submission",
                author = "kiwiheretic",
                body = "My first submission",
                url = "http://reddit.com/r/fake_url1",
                score = 1,
                link_flair_text = "My flair",
                num_comments = 0)
        post.save()
        output =self.plugin.send_method("output_feeds", room=self.room)
        self.assertIn('first submission', output)

        post = Submission(name = "t5_fake2",
                created_at = timezone.make_aware(datetime.datetime.utcnow()),
                subreddit = subreddit,
                title = "second_submission",
                author = "kiwiheretic",
                body = "My second submission",
                url = "http://reddit.com/r/fake_url2",
                score = 1,
                link_flair_text = "My flair",
                num_comments = 0)
        post.save()

        output =self.plugin.send_method("output_feeds", room=self.room)
        self.assertNotIn('first submission', output)
        self.assertIn('second submission', output)

        # Now test deleting subreddit subscriptions
        output = self.plugin.send_command("remove subreddit "+sub_id)
        self.assertIn('deleted successfully', output)

        output = self.plugin.send_command("list subreddits")
        self.assertNotIn('AskPhysics', output)

    def testRedditWithoutRoom(self):
        self.assign_room_permission('fred', self.room, 'room_admin')
        self.set_nick("fred")
        self.login("password1")

        output = self.plugin.send_command("add subreddit /r/askphysics")
        self.assertIn('successfully added subreddit', output)

        # Test subreddit subscription creation
        output = self.plugin.send_command("add subreddit /r/gobbledegookzzz")
        self.assertIn('subreddit does not exist', output)
        
        output = self.plugin.send_command("list subreddits")
        self.assertIn('AskPhysics', output)
        sub_id = re.search(r"(\d+) AskPhysics", output).group(1)


        # create some test data
        subreddit = Subreddits.objects.get(display_name__iexact = "askphysics")
        post = Submission(name = "t5_fake1",
                created_at = timezone.make_aware(datetime.datetime.utcnow()),
                subreddit = subreddit,
                title = "first submission",
                author = "kiwiheretic",
                body = "My first submission",
                url = "http://reddit.com/r/fake_url1",
                score = 1,
                link_flair_text = "My flair",
                num_comments = 0)
        post.save()
        output =self.plugin.send_method("on_timer")
        self.assertIn('first submission', output)

        post = Submission(name = "t5_fake2",
                created_at = timezone.make_aware(datetime.datetime.utcnow()),
                subreddit = subreddit,
                title = "second_submission",
                author = "kiwiheretic",
                body = "My second submission",
                url = "http://reddit.com/r/fake_url2",
                score = 1,
                link_flair_text = "My flair",
                num_comments = 0)
        post.save()

        output =self.plugin.send_method("on_timer")
        self.assertNotIn('first submission', output)
        self.assertIn('second submission', output)

        # Now test deleting subreddit subscriptions
        output = self.plugin.send_command("remove subreddit "+sub_id)
        self.assertIn('deleted successfully', output)

        output = self.plugin.send_command("list subreddits")
        self.assertNotIn('AskPhysics', output)

    def tearDown(self):
        self.fred.delete()
        FeedProgress.objects.all().delete()
        FeedSub.objects.all().delete()
        Submission.objects.all().delete()
        Subreddits.objects.all().delete()

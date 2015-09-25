from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Create your tests here.
from .models import Memo, Folder

class MemoTestCase(TestCase):
    def setUp(self):
        # create test users
        #  https://docs.djangoproject.com/en/1.8/topics/auth/default/#creating-users
        fred = User.objects.create_user("fred", "fred@nowhere.com", "pass123")
        john = User.objects.create_user("john", "john@nowhere.com", "pass456")

    def test_memos(self):
        fred = authenticate(username='fred', password='pass123')
        self.assertIsNotNone(fred)
        john = authenticate(username='john', password='pass456')
        self.assertIsNotNone(john)
        
        Memo.send_memo(john, fred, "This is a test", "Some body text")
        memo_in_inbox = Memo.objects.filter(to_user = fred)
        self.assertIsNotNone(memo_in_inbox)
        memo_in_outbox = Memo.objects.filter(from_user = john)
        self.assertIsNotNone(memo_in_outbox)
        
        # Make sure the right folders are used
        Folder.objects.get(name='inbox',memos__to_user__username="fred")
        Folder.objects.get(name='inbox',memos__from_user__username="john")
        
        # These folder tests should fail
        with self.assertRaises(Folder.DoesNotExist):
            Folder.objects.get(name='inbox',memos__to_user__username="john")
        
        with self.assertRaises(Folder.DoesNotExist):
            Folder.objects.get(name='outbox',memos__from_user__username="fred")

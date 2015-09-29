from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Create your tests here.
from .models import Memo, Folder

class MemoTestCase(TestCase):
    def setUp(self):
        # create test users
        #  https://docs.djangoproject.com/en/1.8/topics/auth/default/#creating-users
        self.u1 = fred = User.objects.create_user("fred", "fred@nowhere.com", "pass123")
        self.u2 = john = User.objects.create_user("john", "john@nowhere.com", "pass456")

    def test_memos(self):
        fred = authenticate(username='fred', password='pass123')
        self.assertIsNotNone(fred)
        john = authenticate(username='john', password='pass456')
        self.assertIsNotNone(john)
        
        Memo.send_memo(john, fred, "This is a test", "Some body text")
        memo_in_inbox = Memo.objects.filter(folder__name='inbox', to_user = fred)
        self.assertIsNotNone(memo_in_inbox)
        memo_in_outbox = Memo.objects.filter(folder__name='outbox', from_user = john)
        self.assertIsNotNone(memo_in_outbox)
        
        # Memos should be cloned, not just referenced!
        self.assertNotEqual(memo_in_inbox, memo_in_outbox)
        
        
        # These folder tests should fail
        with self.assertRaises(Memo.DoesNotExist):
            Memo.objects.get(folder__name='inbox',to_user__username="john")
        
        with self.assertRaises(Memo.DoesNotExist):
            Memo.objects.get(folder__name='outbox',from_user__username="fred")

    def tearDown(self):
        self.u1.delete()
        self.u2.delete()

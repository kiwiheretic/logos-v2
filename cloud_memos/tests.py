from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.test import Client
from django.core.urlresolvers import reverse

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

    def test_views(self):
        c = Client()
        response = c.post('/accounts/login/', {'username': 'john', 'password':'pass456'}, 
            follow=True )
        self.assertEqual(response.status_code, 200)
        
        response = c.post('/memos/new/', {'recipient': 'fred', 
            'subject':'Hi there!',
            'message':'How art thou?'}, 
            follow=True )
        self.assertEqual(response.status_code, 200)
        
        response = c.get('/memos/outbox/')
        # Test memo reachability
        memo = response.context['memos'][0]
        
        response = c.get('/memos/preview/'+str(memo.id))
        self.assertEqual(response.status_code, 200)
        
        
        
    def test_memo_to_self_deleted(self):
        """Test what happens if a memo is sent to self and subsequently deleted
        from outbox.  Does it also incorrectly delete from inbox?"""
        c = Client()
        response = c.post('/accounts/login/', {'username': 'john', 'password':'pass456'}, 
            follow=True )
        self.assertEqual(response.status_code, 200)
        
        response = c.get('/memos/outbox/')
        self.assertFalse (response.context['memos'])
        
        response = c.get('/memos/inbox/')
        self.assertFalse (response.context['memos'])
        
        response = c.post('/memos/new/', {'recipient': 'john', 
            'subject':'Hi there!',
            'message':'How art thou?'}, 
            follow=True )
        self.assertEqual(response.status_code, 200)
    
        response = c.get('/memos/inbox/')
        self.assertTrue (response.context['memos'])
        
        response = c.get('/memos/outbox/')
        self.assertTrue (response.context['memos'])
        
        memo_id = response.context['memos'][0].id
        response = c.get('/memos/preview/'+str(memo_id))
        self.assertEqual(response.status_code, 200)
        
        response = c.get('/memos/trash_memo/'+str(memo_id))
        self.assertEqual(response.status_code, 200)
        
        response = c.post('/memos/trash_memo/'+str(memo_id), {'yes': 'Yes'},  
            follow=True )
        self.assertEqual(response.status_code, 200)
        
        response = c.get('/memos/outbox/')
        self.assertFalse (response.context['memos'])

        response = c.get('/memos/inbox/')
        self.assertTrue (response.context['memos'])
        
    def tearDown(self):
        self.u1.delete()
        self.u2.delete()

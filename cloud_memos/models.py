from __future__ import print_function
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Folder(models.Model):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(User, related_name='folder_user')

    def __unicode__(self):
        return self.name

class Memo(models.Model):
    subject = models.CharField(max_length=30)
    folder = models.ForeignKey('Folder')

    from_user = models.ForeignKey(User, related_name='memo_from')
    to_user = models.ForeignKey(User, related_name='memo_to')
    
    # where to check for read receipts
    corresponding  = models.ForeignKey('Memo', related_name='memo_receipt_to', null=True, blank=True, default = None)
    forwarded_by  = models.ForeignKey('Memo', related_name='memo_forwarded_by', null=True, blank=True, default = None)
    
    # Has the memo been viewed by the recipient yet
    viewed_on = models.DateTimeField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add = True)
    text = models.TextField()

    @staticmethod
    def send_memo(sender, recipient, subject, message):
        memo = Memo(to_user=recipient, 
                from_user=sender, 
                subject=subject, 
                text=message)
        outbox = Folder.objects.get(user=sender, name='outbox')
        memo.folder = outbox
        memo.save()
        m1 = memo.pk
        
        # now clone the memo
        memo.id = None
        
        inbox = Folder.objects.get(user=recipient, name='inbox')
        memo.folder = inbox
        other_memo = Memo.objects.get(pk = m1)
        memo.corresponding = other_memo
        memo.save()
        
        other_memo.corresponding = memo
        other_memo.save()
        
@receiver(post_save, sender=User)
def user_post_save_handler(sender, instance, created, **kwargs):
    if created:
        user = instance
        print ("creating inbox/outbox for "+user.username)
        inbox = Folder(name='inbox', user=user)
        inbox.save()
        outbox = Folder(name='outbox', user=user)
        outbox.save()
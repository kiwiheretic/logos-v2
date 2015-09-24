from __future__ import print_function
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Folder(models.Model):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(User, related_name='folder_user')
    memos = models.ManyToManyField('Memo')

# class Conversation(models.Model):
    # title = models.CharField(max_length=30)

class Memo(models.Model):
    subject = models.CharField(max_length=30)
    # conversation = models.ForeignKey(Conversation)
    from_user = models.ForeignKey(User, related_name='memos_from')
    to_user = models.ForeignKey(User, related_name='memos_to')
    in_reply_to  = models.ForeignKey('Memo', null=True, blank=True, default = None)
    
    # Has the memo been viewed by the recipient yet
    viewed = models.DateTimeField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add = True)
    text = models.TextField()

@receiver(post_save, sender=User)
def user_post_save_handler(sender, instance, created, **kwargs):
    if created:
        user = instance
        print ("creating inbox/outbox for "+user.username)
        inbox = Folder(name='inbox', user=user)
        inbox.save()
        outbox = Folder(name='outbox', user=user)
        outbox.save()
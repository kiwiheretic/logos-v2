from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Folder(models.Model):
    name = models.CharField(max_length=30)

class Conversation(models.Model):
    title = models.CharField(max_length=30)

class Memo(models.Model):
    conversation = models.ForeignKey(Conversation)
    from_user = models.ForeignKey(User, related_name='memos_from')
    to_user = models.ForeignKey(User, related_name='memos_to')
    in_reply_to  = models.ForeignKey('Memo', null=True, blank=True, default = None)
    
    # note_type is something like "memo", "web-page", ... etc
    created = models.DateTimeField(auto_now_add = True)
    text = models.TextField()

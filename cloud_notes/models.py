from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.
class Folder(models.Model):
    name = models.CharField(max_length=30)
    # Folders really need to be specific to User (TO DO)
    user = models.ForeignKey(User)

class Note(models.Model):
    user = models.ForeignKey(User)
    folder = models.ForeignKey(Folder)
    title = models.CharField(max_length=120)
    # note_type is something like "memo", "web-page", ... etc
    note_type = models.CharField(blank=True, default="", max_length=15)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    note = models.TextField()

@receiver(post_save, sender=User)
def new_user_handler(sender, instance, created, **kwargs):
    if created:
        user = instance
        print ("creating main notes folder for "+user.username)
        main = Folder(name="Main", user=user)
        main.save()
        

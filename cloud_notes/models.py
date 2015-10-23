from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

import re

# Create your models here.
class Folder(models.Model):
    name = models.CharField(max_length=30)
    # Folders really need to be specific to User (TO DO)
    user = models.ForeignKey(User)
    def __unicode__(self):
        return u"Folder %d" % (self.id, )

class Note(models.Model):
    user = models.ForeignKey(User)
    folder = models.ForeignKey(Folder)
    title = models.CharField(max_length=120)
    # note_type is something like "memo", "web-page", ... etc
    note_type = models.CharField(blank=True, default="", max_length=15)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    note = models.TextField()

    def add_tags(self):
        words = re.split(r'\s+', self.note)
        for wrd in words:
            if re.match(r'^#[a-zA-Z0-9-]+$', wrd):
                obj, created = HashTags.objects.get_or_create(hash_tag = wrd.lower(),user = self.user )
                obj.notes.add(self)

    def __unicode__(self):
        return u"{} \"{}\"...".format(self.id, self.title[0:10])
        
        
class HashTags(models.Model):
    user = models.ForeignKey(User)
    hash_tag = models.CharField(max_length=30, db_index = True)
    created_at = models.DateTimeField(auto_now_add = True)
    notes = models.ManyToManyField(Note)

    def __unicode__(self):
        return u"%s" % (self.hash_tag, )


@receiver(post_save, sender=Note)
def note_post_save_handler(sender, instance, created, **kwargs):
    for tag in HashTags.objects.filter(user = instance.user):
        tag.notes.remove(instance)
    instance.add_tags()
    
@receiver(post_save, sender=User)
def new_user_handler(sender, instance, created, **kwargs):
    if created:
        user = instance
        print ("creating main notes folder for "+user.username)
        main = Folder(name="Main", user=user)
        main.save()
        trash = Folder(name="Trash", user=user)
        trash.save()
        

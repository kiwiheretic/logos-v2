from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Folder(models.Model):
    name = models.CharField(max_length=30)

class Note(models.Model):
    user = models.ForeignKey(User)
    folder = models.ForeignKey(Folder)
    title = models.CharField(max_length=120)
    # note_type is something like "memo", "web-page", ... etc
    note_type = models.CharField(blank=True, default="", max_length=15)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    note = models.TextField()

# We may be able to have a merge tag system where tags 
# can be consolidated with existing tags
#class Tag(models.Model):
#    name = models.CharField(max_length=30)
#    note = models.ManyToManyField(Note)
    
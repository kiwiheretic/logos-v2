from django.contrib.auth.models import User
from django.db import models

from oauth2client.django_orm import FlowField, CredentialsField 


# Create your models here.

class SiteModel(models.Model):
    client_id = models.CharField(max_length=200)
    client_secret = models.CharField(max_length=200)

class FlowModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    flow = FlowField()

class CredentialsModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    credential = CredentialsField()


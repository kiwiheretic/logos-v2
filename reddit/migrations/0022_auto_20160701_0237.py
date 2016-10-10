# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0021_redditcredentials_reddit_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendingsubmissions',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]

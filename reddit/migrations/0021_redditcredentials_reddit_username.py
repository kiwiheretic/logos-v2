# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0020_pendingsubmissions_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='redditcredentials',
            name='reddit_username',
            field=models.CharField(max_length=50, null=True),
        ),
    ]

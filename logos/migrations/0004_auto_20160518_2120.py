# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logos', '0003_auto_20160217_2158'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CapturedUrls',
        ),
        migrations.RemoveField(
            model_name='reportedtweets',
            name='tweet',
        ),
        migrations.DeleteModel(
            name='TwitterFollows',
        ),
        migrations.DeleteModel(
            name='ReportedTweets',
        ),
        migrations.DeleteModel(
            name='TwitterStatuses',
        ),
    ]

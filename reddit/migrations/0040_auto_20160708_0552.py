# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0039_auto_20160708_0543'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='feedprogress',
            unique_together=set([('feed', 'subreddit')]),
        ),
    ]

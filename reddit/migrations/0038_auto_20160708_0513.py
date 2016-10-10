# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0037_auto_20160708_0455'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedprogress',
            name='last_processed',
        ),
        migrations.AddField(
            model_name='feedsub',
            name='last_processed',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='feedprogress',
            name='feed',
            field=models.ForeignKey(to='reddit.FeedSub'),
        ),
    ]

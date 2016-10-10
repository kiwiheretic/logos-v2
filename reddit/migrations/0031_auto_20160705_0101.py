# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0030_auto_20160705_0046'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedprogress',
            name='subreddit',
            field=models.ForeignKey(default=0, to='reddit.Subreddits'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='feedprogress',
            name='processed_to',
            field=models.DateTimeField(null=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0026_feedsub_frequency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='irctarget',
            name='feed_sub',
        ),
        migrations.RemoveField(
            model_name='subreddittarget',
            name='feed_sub',
        ),
        migrations.RemoveField(
            model_name='subreddittarget',
            name='subreddit',
        ),
        migrations.AddField(
            model_name='feedsub',
            name='subreddits',
            field=models.ManyToManyField(related_name='feeds', to='reddit.Subreddits'),
        ),
        migrations.AddField(
            model_name='feedsub',
            name='target_irc',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='feedsub',
            name='target_sub',
            field=models.ForeignKey(to='reddit.Subreddits', null=True),
        ),
        migrations.DeleteModel(
            name='IRCTarget',
        ),
        migrations.DeleteModel(
            name='SubredditTarget',
        ),
    ]

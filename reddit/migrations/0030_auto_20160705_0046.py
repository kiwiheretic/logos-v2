# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0029_auto_20160704_0421'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedProgress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('processed_to', models.DateTimeField()),
                ('processed', models.IntegerField()),
                ('feed', models.ForeignKey(to='reddit.FeedSub')),
            ],
        ),
        migrations.RemoveField(
            model_name='feedsubredditsub',
            name='feed',
        ),
        migrations.RemoveField(
            model_name='feedsubredditsub',
            name='subreddit',
        ),
        migrations.DeleteModel(
            name='FeedSubredditSub',
        ),
    ]

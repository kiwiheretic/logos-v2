# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reddit', '0024_auto_20160701_0330'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedSub',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FeedSubredditSub',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('processed', models.DateTimeField(null=True)),
                ('feed', models.ForeignKey(to='reddit.FeedSub')),
            ],
        ),
        migrations.CreateModel(
            name='IRCTarget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.CharField(max_length=100)),
                ('room', models.CharField(max_length=50)),
                ('feed_sub', models.ForeignKey(to='reddit.FeedSub')),
            ],
        ),
        migrations.CreateModel(
            name='SubredditTarget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feed_sub', models.ForeignKey(to='reddit.FeedSub')),
            ],
        ),
        migrations.AlterModelOptions(
            name='subreddits',
            options={'ordering': ['display_name']},
        ),
        migrations.AddField(
            model_name='subreddittarget',
            name='subreddit',
            field=models.ForeignKey(to='reddit.Subreddits'),
        ),
        migrations.AddField(
            model_name='feedsubredditsub',
            name='subreddit',
            field=models.ForeignKey(to='reddit.Subreddits'),
        ),
    ]

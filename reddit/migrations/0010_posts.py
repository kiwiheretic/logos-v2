# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0009_auto_20160619_2256'),
    ]

    operations = [
        migrations.CreateModel(
            name='Posts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('created_at', models.DateTimeField()),
                ('title', models.CharField(max_length=250)),
                ('body', models.TextField()),
                ('url', models.URLField()),
                ('score', models.IntegerField()),
                ('link_flair_text', models.CharField(max_length=50)),
                ('num_comments', models.IntegerField()),
                ('subreddit', models.ForeignKey(to='reddit.Subreddits')),
            ],
        ),
    ]

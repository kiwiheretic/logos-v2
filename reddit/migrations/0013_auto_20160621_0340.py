# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0012_auto_20160620_0256'),
    ]

    operations = [
        migrations.CreateModel(
            name='Submissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('created_at', models.DateTimeField()),
                ('title', models.CharField(max_length=250)),
                ('author', models.CharField(max_length=50)),
                ('body', models.TextField()),
                ('url', models.URLField()),
                ('score', models.IntegerField()),
                ('link_flair_text', models.CharField(max_length=50, null=True)),
                ('num_comments', models.IntegerField()),
                ('subreddit', models.ForeignKey(to='reddit.Subreddits')),
            ],
        ),
        migrations.RemoveField(
            model_name='posts',
            name='subreddit',
        ),
        migrations.DeleteModel(
            name='Posts',
        ),
    ]

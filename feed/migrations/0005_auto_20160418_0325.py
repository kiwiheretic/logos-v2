# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('feed', '0004_auto_20160418_0027'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.CharField(max_length=50)),
                ('room', models.CharField(max_length=50)),
                ('periodic', models.CharField(default=b'', max_length=15, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('last_read', models.DateTimeField()),
                ('feed', models.ForeignKey(to='feed.Feed')),
                ('user_added', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='cache',
            name='actioned',
        ),
        migrations.RemoveField(
            model_name='cache',
            name='network',
        ),
        migrations.RemoveField(
            model_name='cache',
            name='room',
        ),
        migrations.RemoveField(
            model_name='feed',
            name='network',
        ),
        migrations.RemoveField(
            model_name='feed',
            name='periodic',
        ),
        migrations.RemoveField(
            model_name='feed',
            name='room',
        ),
        migrations.RemoveField(
            model_name='feed',
            name='user_added',
        ),
    ]

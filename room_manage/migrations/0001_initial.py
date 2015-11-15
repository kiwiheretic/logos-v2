# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DownVotes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.TextField()),
                ('room', models.TextField()),
                ('nick_mask', models.CharField(max_length=80)),
                ('downvoting_nick', models.CharField(max_length=40)),
                ('downvote_datetime', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NickProtection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.TextField()),
                ('room', models.TextField()),
                ('protect_registered', models.BooleanField(default=False)),
                ('downvote_immunity', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Penalty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.TextField()),
                ('room', models.TextField()),
                ('nick_mask', models.CharField(max_length=80)),
                ('begin', models.DateTimeField(auto_now_add=True)),
                ('end', models.DateTimeField(auto_now_add=True)),
                ('kick', models.BooleanField(default=False)),
                ('mute', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

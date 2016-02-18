# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotsRunning',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pid', models.IntegerField()),
                ('started', models.DateTimeField(auto_now_add=True)),
                ('rpc', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CapturedUrls',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('nick', models.CharField(max_length=90)),
                ('room', models.CharField(max_length=60)),
                ('url', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NetworkPermissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.TextField()),
            ],
            options={
                'permissions': (('bot_admin', 'Create user logins and assign permissions'), ('activate_plugins', 'Can activate/deactivate plugins network wide'), ('join_or_part_room', 'Join or part bot to rooms'), ('irc_cmd', 'Issue arbitrary command to bot'), ('set_pvt_version', 'Set bible version default in private chat window'), ('change_pvt_trigger', 'Set trigger used in private chat window'), ('change_nick', 'Can issue a bot nick change command'), ('warn_user', 'Warn a user of their behaviour')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NetworkPlugins',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.TextField()),
                ('loaded', models.BooleanField(default=False)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OptionLabels',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.CharField(max_length=15)),
                ('display_order', models.PositiveSmallIntegerField()),
                ('label', models.CharField(max_length=40)),
                ('option_name', models.CharField(max_length=15)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Plugins',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField()),
                ('system', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReportedTweets',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.CharField(max_length=60)),
                ('room', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoomOptions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.TextField()),
                ('room', models.TextField()),
                ('option', models.TextField()),
                ('value', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'room_options',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoomPermissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.TextField()),
                ('room', models.TextField()),
            ],
            options={
                'permissions': (('room_admin', 'Assign permissions to existing users of own room'), ('change_trigger', 'Change trigger'), ('set_default_translation', 'Set default room translation'), ('set_verse_limits', 'Set room verse limits'), ('set_greeting', 'Set room greeting message'), ('can_speak', 'Speak through bot'), ('enable_plugins', 'Can enable or disable room plugins'), ('kick_user', 'Can kick user'), ('ban_user', 'Can ban user'), ('room_op', 'Bot can op'), ('twitter_op', 'Can add or remove twitter follows')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoomPlugins',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('room', models.TextField()),
                ('enabled', models.BooleanField(default=False)),
                ('net', models.ForeignKey(to='logos.NetworkPlugins')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('option', models.TextField()),
                ('value', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TwitterFollows',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.CharField(max_length=60)),
                ('room', models.CharField(max_length=30)),
                ('screen_name', models.CharField(max_length=60)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TwitterStatuses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('twitter_id', models.DecimalField(unique=True, max_digits=25, decimal_places=0)),
                ('created_at', models.DateTimeField()),
                ('screen_name', models.CharField(max_length=60)),
                ('text', models.CharField(max_length=260)),
                ('url', models.CharField(max_length=200, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='reportedtweets',
            name='tweet',
            field=models.ForeignKey(to='logos.TwitterStatuses'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='networkplugins',
            name='plugin',
            field=models.ForeignKey(to='logos.Plugins'),
            preserve_default=True,
        ),
    ]

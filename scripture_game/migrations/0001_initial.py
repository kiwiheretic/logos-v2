# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GameGames',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('ref', models.TextField(blank=True)),
                ('scripture', models.TextField(blank=True)),
                ('num_rounds', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GameSolveAttempts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('attempt', models.TextField(blank=True)),
                ('reason', models.TextField(blank=True)),
                ('game', models.ForeignKey(to='scripture_game.GameGames')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GameUsers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nick', models.TextField(blank=True)),
                ('host', models.TextField(blank=True)),
                ('game', models.ForeignKey(to='scripture_game.GameGames')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scriptures',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.TextField()),
                ('verse', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='gamesolveattempts',
            name='user',
            field=models.ForeignKey(to='scripture_game.GameUsers'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gamegames',
            name='winner',
            field=models.ForeignKey(to='scripture_game.GameUsers', null=True),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.CharField(max_length=50)),
                ('room', models.CharField(max_length=50)),
                ('guid', models.CharField(unique=True, max_length=80)),
                ('link', models.URLField()),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('published', models.DateTimeField()),
                ('feed', models.ForeignKey(to='feed.Feed')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

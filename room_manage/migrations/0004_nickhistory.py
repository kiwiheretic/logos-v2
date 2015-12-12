# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('room_manage', '0003_auto_20151211_1731'),
    ]

    operations = [
        migrations.CreateModel(
            name='NickHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.TextField()),
                ('room', models.TextField()),
                ('nick', models.CharField(max_length=40)),
                ('host_mask', models.CharField(max_length=80)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

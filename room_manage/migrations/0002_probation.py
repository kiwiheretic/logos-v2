# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('room_manage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Probation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.TextField()),
                ('room', models.TextField()),
                ('nick_mask', models.CharField(max_length=80)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

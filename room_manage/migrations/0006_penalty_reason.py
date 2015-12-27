# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('room_manage', '0005_nickhistory_time_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='penalty',
            name='reason',
            field=models.CharField(max_length=80, null=True, blank=True),
            preserve_default=True,
        ),
    ]

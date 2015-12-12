# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('room_manage', '0004_nickhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='nickhistory',
            name='time_seen',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
    ]

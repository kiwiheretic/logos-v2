# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('room_manage', '0009_auto_20160523_2340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nickhistory',
            name='time_seen',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
    ]

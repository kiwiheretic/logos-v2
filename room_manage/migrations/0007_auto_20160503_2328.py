# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room_manage', '0006_penalty_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nickhistory',
            name='network',
            field=models.TextField(db_index=True),
        ),
        migrations.AlterField(
            model_name='nickhistory',
            name='nick',
            field=models.CharField(max_length=40, db_index=True),
        ),
    ]

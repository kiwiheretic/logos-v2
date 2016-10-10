# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0014_auto_20160621_0344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='created_at',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='score',
            field=models.IntegerField(db_index=True),
        ),
    ]

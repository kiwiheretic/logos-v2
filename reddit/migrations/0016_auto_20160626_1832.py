# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0015_auto_20160626_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='body',
            field=models.TextField(null=True),
        ),
    ]

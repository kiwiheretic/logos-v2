# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0040_auto_20160708_0552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedprogress',
            name='processed',
            field=models.IntegerField(default=0),
        ),
    ]

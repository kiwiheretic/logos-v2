# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0038_auto_20160708_0513'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='submission',
            options={'ordering': ('created_at',)},
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0002_cache'),
    ]

    operations = [
        migrations.AddField(
            model_name='cache',
            name='actioned',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

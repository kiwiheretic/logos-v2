# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0003_cache_actioned'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cache',
            name='description',
            field=models.TextField(null=True),
        ),
    ]

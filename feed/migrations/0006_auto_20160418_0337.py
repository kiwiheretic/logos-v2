# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0005_auto_20160418_0325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='feedurl',
            field=models.URLField(unique=True),
        ),
    ]

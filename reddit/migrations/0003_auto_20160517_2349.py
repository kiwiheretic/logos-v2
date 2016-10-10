# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0002_auto_20160517_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redditcredentials',
            name='token_data',
            field=models.BinaryField(),
        ),
    ]

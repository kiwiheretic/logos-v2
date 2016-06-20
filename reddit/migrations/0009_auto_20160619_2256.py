# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0008_auto_20160619_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subreddits',
            name='name',
            field=models.CharField(unique=True, max_length=15),
        ),
    ]

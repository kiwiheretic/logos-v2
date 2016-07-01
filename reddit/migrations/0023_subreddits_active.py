# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0022_auto_20160701_0237'),
    ]

    operations = [
        migrations.AddField(
            model_name='subreddits',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]

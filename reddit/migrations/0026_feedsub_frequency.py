# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0025_auto_20160701_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedsub',
            name='frequency',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]

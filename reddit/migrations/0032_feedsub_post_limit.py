# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0031_auto_20160705_0101'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedsub',
            name='post_limit',
            field=models.IntegerField(default=1),
        ),
    ]

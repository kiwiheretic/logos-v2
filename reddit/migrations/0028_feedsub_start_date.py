# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0027_auto_20160703_2325'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedsub',
            name='start_date',
            field=models.DateTimeField(null=True),
        ),
    ]

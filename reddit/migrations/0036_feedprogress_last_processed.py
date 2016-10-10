# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0035_auto_20160706_2229'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedprogress',
            name='last_processed',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 8, 4, 52, 33, 30584, tzinfo=utc)),
            preserve_default=False,
        ),
    ]

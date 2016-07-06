# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0033_auto_20160705_0151'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pendingsubmissions',
            name='submitted',
        ),
        migrations.AddField(
            model_name='pendingsubmissions',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 6, 7, 45, 41, 620621, tzinfo=utc), db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pendingsubmissions',
            name='uploaded_at',
            field=models.DateTimeField(null=True, db_index=True),
        ),
    ]

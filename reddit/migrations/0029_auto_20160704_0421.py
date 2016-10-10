# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0028_feedsub_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedsubredditsub',
            name='processed_to',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 4, 4, 21, 6, 260141, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='feedsub',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 4, 4, 21, 23, 67240, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='feedsubredditsub',
            name='processed',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]

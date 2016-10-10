# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0036_feedprogress_last_processed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedprogress',
            name='feed',
            field=models.OneToOneField(to='reddit.FeedSub'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0003_auto_20160517_2349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redditcredentials',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

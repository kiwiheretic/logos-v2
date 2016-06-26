# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0017_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='score',
            field=models.IntegerField(default=0, db_index=True),
            preserve_default=False,
        ),
    ]

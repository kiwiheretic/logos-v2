# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0011_auto_20160620_0225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='link_flair_text',
            field=models.CharField(max_length=50, null=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0023_subreddits_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingsubmissions',
            name='url',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='pendingsubmissions',
            name='body',
            field=models.TextField(null=True),
        ),
    ]

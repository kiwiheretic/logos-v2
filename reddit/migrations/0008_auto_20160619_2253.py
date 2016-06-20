# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0007_auto_20160619_2130'),
    ]

    operations = [
        migrations.AddField(
            model_name='subreddits',
            name='display_name',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subreddits',
            name='name',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='subreddits',
            name='url',
            field=models.CharField(max_length=80),
        ),
    ]

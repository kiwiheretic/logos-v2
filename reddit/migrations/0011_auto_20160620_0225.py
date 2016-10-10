# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0010_posts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='name',
            field=models.CharField(unique=True, max_length=30),
        ),
    ]

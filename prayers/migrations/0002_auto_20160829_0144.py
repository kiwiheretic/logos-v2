# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prayers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prayer',
            name='timestamp',
            field=models.DateTimeField(),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gcalendar', '0002_sitemodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitemodel',
            name='client_id',
            field=models.CharField(max_length=200),
        ),
    ]

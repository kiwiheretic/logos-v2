# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logos', '0004_auto_20160518_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='networkpermissions',
            name='network',
            field=models.TextField(unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='roompermissions',
            unique_together=set([('network', 'room')]),
        ),
    ]

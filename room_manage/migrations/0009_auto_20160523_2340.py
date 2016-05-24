# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room_manage', '0008_nicksummary'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='nicksummary',
            index_together=set([('network', 'nick'), ('network', 'host_mask')]),
        ),
    ]

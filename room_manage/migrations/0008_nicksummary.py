# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room_manage', '0007_auto_20160503_2328'),
    ]

    operations = [
        migrations.CreateModel(
            name='NickSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.TextField(db_index=True)),
                ('nick', models.CharField(max_length=40, db_index=True)),
                ('host_mask', models.CharField(max_length=80)),
                ('last_seen', models.DateTimeField()),
            ],
        ),
    ]

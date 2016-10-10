# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Prayer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.CharField(max_length=60)),
                ('room', models.CharField(max_length=60)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('nick', models.CharField(max_length=90)),
                ('request', models.CharField(max_length=200)),
            ],
        ),
    ]

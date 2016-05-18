# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('gcalendar', '0003_auto_20160213_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credentialsmodel',
            name='id',
            field=models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='flowmodel',
            name='id',
            field=models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0034_auto_20160706_0745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedsub',
            name='target_irc',
            field=models.ForeignKey(to='logos.RoomPermissions', null=True),
        ),
    ]

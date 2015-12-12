# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('room_manage', '0002_probation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='probation',
            old_name='nick_mask',
            new_name='host_mask',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logos', '0002_useroptions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='useroptions',
            old_name='username',
            new_name='user',
        ),
    ]

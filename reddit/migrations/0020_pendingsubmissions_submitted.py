# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0019_pendingsubmissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingsubmissions',
            name='submitted',
            field=models.BooleanField(default=False),
        ),
    ]

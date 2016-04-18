# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0006_auto_20160418_0337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedsubscription',
            name='last_read',
            field=models.DateTimeField(null=True),
        ),
    ]

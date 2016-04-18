# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0008_auto_20160418_0507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cache',
            name='guid',
            field=models.CharField(unique=True, max_length=80, db_index=True),
        ),
        migrations.AlterIndexTogether(
            name='cacheviews',
            index_together=set([('network', 'room')]),
        ),
        migrations.AlterIndexTogether(
            name='feedsubscription',
            index_together=set([('network', 'room')]),
        ),
    ]

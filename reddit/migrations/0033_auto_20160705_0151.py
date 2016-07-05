# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0032_feedsub_post_limit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedprogress',
            name='processed_to',
            field=models.ForeignKey(to='reddit.Submission', null=True),
        ),
    ]

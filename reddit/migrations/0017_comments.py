# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0016_auto_20160626_1832'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('parent_thing', models.CharField(max_length=30)),
                ('created_at', models.DateTimeField(db_index=True)),
                ('author', models.CharField(max_length=50)),
                ('body', models.TextField()),
                ('submission', models.ForeignKey(to='reddit.Submission')),
            ],
        ),
    ]

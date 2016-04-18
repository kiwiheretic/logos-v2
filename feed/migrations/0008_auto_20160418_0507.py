# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0007_auto_20160418_0350'),
    ]

    operations = [
        migrations.CreateModel(
            name='CacheViews',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.CharField(max_length=50)),
                ('room', models.CharField(max_length=50)),
                ('cache', models.ForeignKey(to='feed.Cache')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='feedsubscription',
            name='last_read',
        ),
    ]

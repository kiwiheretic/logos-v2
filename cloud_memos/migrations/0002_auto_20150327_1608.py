# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cloud_memos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='memo',
            name='title',
        ),
        migrations.AddField(
            model_name='memo',
            name='conversation',
            field=models.ForeignKey(default=1, to='cloud_memos.Conversation'),
            preserve_default=False,
        ),
    ]

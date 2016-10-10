# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reddit', '0041_auto_20160708_0601'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingComments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent_thing', models.CharField(max_length=30)),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(db_index=True)),
                ('uploaded_at', models.DateTimeField(null=True, db_index=True)),
                ('submission', models.ForeignKey(to='reddit.Submission')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

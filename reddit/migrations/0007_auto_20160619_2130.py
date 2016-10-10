# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reddit', '0006_auto_20160518_0036'),
    ]

    operations = [
        migrations.CreateModel(
            name='MySubreddits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subreddits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('url', models.URLField()),
            ],
        ),
        migrations.AddField(
            model_name='mysubreddits',
            name='subreddits',
            field=models.ManyToManyField(related_name='subscriptions', to='reddit.Subreddits'),
        ),
        migrations.AddField(
            model_name='mysubreddits',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]

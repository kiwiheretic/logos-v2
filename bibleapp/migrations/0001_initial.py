# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BibleBooks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('book_idx', models.IntegerField()),
                ('long_book_name', models.TextField()),
                ('canonical', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'bible_books',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BibleColours',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.TextField()),
                ('room', models.TextField()),
                ('element', models.TextField()),
                ('mirc_colour', models.TextField()),
            ],
            options={
                'db_table': 'bible_colours',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BibleConcordance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('chapter', models.IntegerField()),
                ('verse', models.IntegerField()),
                ('word_id', models.IntegerField()),
                ('word', models.CharField(max_length=60)),
                ('book', models.ForeignKey(to='bibleapp.BibleBooks')),
            ],
            options={
                'db_table': 'bible_concordance',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BibleDict',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('strongs', models.CharField(max_length=10, db_index=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'bible_dict',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BibleStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trans_idx', models.IntegerField()),
                ('word', models.CharField(max_length=60)),
                ('count', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BibleTranslations',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=10)),
            ],
            options={
                'db_table': 'bible_translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BibleVerses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('chapter', models.IntegerField()),
                ('verse', models.IntegerField()),
                ('verse_text', models.TextField()),
                ('book', models.ForeignKey(to='bibleapp.BibleBooks')),
                ('trans', models.ForeignKey(to='bibleapp.BibleTranslations')),
            ],
            options={
                'db_table': 'bible_verses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='XRefs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('primary_book', models.CharField(max_length=15)),
                ('primary_chapter', models.IntegerField()),
                ('primary_verse', models.IntegerField()),
                ('xref_book1', models.CharField(max_length=15)),
                ('xref_chapter1', models.IntegerField()),
                ('xref_verse1', models.IntegerField()),
                ('xref_book2', models.CharField(max_length=15, null=True, blank=True)),
                ('xref_chapter2', models.IntegerField(null=True, blank=True)),
                ('xref_verse2', models.IntegerField(null=True, blank=True)),
                ('votes', models.IntegerField()),
            ],
            options={
                'db_table': 'xrefs',
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='bibleverses',
            index_together=set([('trans', 'book', 'chapter', 'verse')]),
        ),
        migrations.AlterIndexTogether(
            name='biblestats',
            index_together=set([('trans_idx', 'count')]),
        ),
        migrations.AddField(
            model_name='bibleconcordance',
            name='trans',
            field=models.ForeignKey(to='bibleapp.BibleTranslations'),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='bibleconcordance',
            index_together=set([('trans', 'book', 'chapter', 'verse', 'word_id'), ('trans', 'word', 'chapter', 'verse'), ('trans', 'word'), ('trans', 'word', 'chapter')]),
        ),
        migrations.AddField(
            model_name='biblebooks',
            name='trans',
            field=models.ForeignKey(to='bibleapp.BibleTranslations'),
            preserve_default=True,
        ),
    ]

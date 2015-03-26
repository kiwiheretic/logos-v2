# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('pybb_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True, blank=True)),
        ))
        db.send_create_signal('pybb', ['Category'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('pybb_category')


    models = {
        'pybb.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['pybb']
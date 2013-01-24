# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HealthFacilityIdMap'
        db.create_table('fred_consumer_healthfacilityidmap', (
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('fred_consumer', ['HealthFacilityIdMap'])


    def backwards(self, orm):
        # Deleting model 'HealthFacilityIdMap'
        db.delete_table('fred_consumer_healthfacilityidmap')


    models = {
        'fred_consumer.fredconfig': {
            'Meta': {'object_name': 'FredConfig'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'fred_consumer.healthfacilityidmap': {
            'Meta': {'object_name': 'HealthFacilityIdMap'},
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['fred_consumer']
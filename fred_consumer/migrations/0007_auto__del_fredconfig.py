# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'FredConfig'
        db.delete_table('fred_consumer_fredconfig')


    def backwards(self, orm):
        # Adding model 'FredConfig'
        db.create_table('fred_consumer_fredconfig', (
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal('fred_consumer', ['FredConfig'])


    models = {
        'fred_consumer.failure': {
            'Meta': {'object_name': 'Failure'},
            'action': ('django.db.models.fields.TextField', [], {'default': "'GET'"}),
            'exception': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'fred_consumer.healthfacilityidmap': {
            'Meta': {'object_name': 'HealthFacilityIdMap'},
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'})
        },
        'fred_consumer.jobstatus': {
            'Meta': {'object_name': 'JobStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['fred_consumer']
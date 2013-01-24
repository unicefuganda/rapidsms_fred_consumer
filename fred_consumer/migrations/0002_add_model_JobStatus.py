# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'JobStatus'
        db.create_table('fred_consumer_jobstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('job_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('fred_consumer', ['JobStatus'])


    def backwards(self, orm):
        # Deleting model 'JobStatus'
        db.delete_table('fred_consumer_jobstatus')


    models = {
        'fred_consumer.fredconfig': {
            'Meta': {'object_name': 'FredConfig'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'fred_consumer.healthfacilityidmap': {
            'Meta': {'object_name': 'HealthFacilityIdMap'},
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'fred_consumer.jobstatus': {
            'Meta': {'object_name': 'JobStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['fred_consumer']
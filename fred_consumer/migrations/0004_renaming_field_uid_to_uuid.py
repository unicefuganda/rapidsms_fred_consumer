# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_column('fred_consumer_healthfacilityidmap', 'uid', 'uuid')

    def backwards(self, orm):
        db.rename_column('fred_consumer_healthfacilityidmap', 'uuid', 'uid')

    models = {
        'fred_consumer.fredconfig': {
            'Meta': {'object_name': 'FredConfig'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['fred_consumer']
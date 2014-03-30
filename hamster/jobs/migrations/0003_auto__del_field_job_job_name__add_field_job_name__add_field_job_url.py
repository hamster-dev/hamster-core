# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Job.job_name'
        db.delete_column(u'jobs_job', 'job_name')

        # Adding field 'Job.name'
        db.add_column(u'jobs_job', 'name',
                      self.gf('django.db.models.fields.CharField')(default='unset', max_length=80),
                      keep_default=False)

        # Adding field 'Job.url'
        db.add_column(u'jobs_job', 'url',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Job.job_name'
        db.add_column(u'jobs_job', 'job_name',
                      self.gf('django.db.models.fields.CharField')(default='unset', max_length=80),
                      keep_default=False)

        # Deleting field 'Job.name'
        db.delete_column(u'jobs_job', 'name')

        # Deleting field 'Job.url'
        db.delete_column(u'jobs_job', 'url')


    models = {
        u'jobs.job': {
            'Meta': {'object_name': 'Job'},
            'disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['jobs']
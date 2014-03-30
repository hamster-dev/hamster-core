# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Build'
        db.create_table(u'builds_build', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jobs.Job'])),
            ('executed_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('commit', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('output', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'builds', ['Build'])

        # Adding model 'Artifact'
        db.create_table(u'builds_artifact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('build', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['builds.Build'])),
            ('artifact', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'builds', ['Artifact'])


    def backwards(self, orm):
        # Deleting model 'Build'
        db.delete_table(u'builds_build')

        # Deleting model 'Artifact'
        db.delete_table(u'builds_artifact')


    models = {
        u'builds.artifact': {
            'Meta': {'object_name': 'Artifact'},
            'artifact': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'build': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['builds.Build']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'builds.build': {
            'Meta': {'object_name': 'Build'},
            'commit': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'executed_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jobs.Job']"}),
            'output': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'jobs.job': {
            'Meta': {'object_name': 'Job'},
            'disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['builds']
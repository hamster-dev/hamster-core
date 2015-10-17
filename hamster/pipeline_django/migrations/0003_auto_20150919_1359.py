# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pipeline_django', '0002_pipelineeventhandler_composition'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventSubscriber',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('events', jsonfield.fields.JSONField(default=[])),
                ('criteria', jsonfield.fields.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('actions', jsonfield.fields.JSONField()),
                ('composition', models.CharField(default='chain', max_length=32, choices=[('chain', 'chain'), ('group', 'group')])),
            ],
        ),
        migrations.DeleteModel(
            name='PipelineEventHandler',
        ),
        migrations.AddField(
            model_name='eventsubscriber',
            name='pipeline',
            field=models.ForeignKey(to='pipeline_django.Pipeline'),
        ),
    ]

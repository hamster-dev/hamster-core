# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PipelineEventHandler',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('events', jsonfield.fields.JSONField(default=[])),
                ('criteria', jsonfield.fields.JSONField(null=True)),
                ('actions', jsonfield.fields.JSONField()),
                ('enabled', models.BooleanField(default=True)),
                ('app_name', models.CharField(max_length=64, blank=True)),
            ],
        ),
    ]

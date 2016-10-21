# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import yamlfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventSubscriber',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('data', yamlfield.fields.YAMLField()),
            ],
        ),
    ]

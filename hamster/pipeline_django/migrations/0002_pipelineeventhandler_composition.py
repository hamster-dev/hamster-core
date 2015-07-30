# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pipeline_django', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipelineeventhandler',
            name='composition',
            field=models.CharField(max_length=32, default='chain'),
        ),
    ]

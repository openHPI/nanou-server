# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-03-01 19:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0002_surveys_completed_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='secondary_link',
            field=models.URLField(blank=True, null=True),
        ),
    ]
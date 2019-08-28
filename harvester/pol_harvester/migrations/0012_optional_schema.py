# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-28 12:08
from __future__ import unicode_literals

from django.db import migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pol_harvester', '0011_postgres_model_ordering'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arrangement',
            name='schema',
            field=json_field.fields.JSONField(blank=True, default=dict, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='article',
            name='schema',
            field=json_field.fields.JSONField(blank=True, default=dict, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='schema',
            field=json_field.fields.JSONField(blank=True, default=dict, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='corpus',
            name='schema',
            field=json_field.fields.JSONField(blank=True, default=dict, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='document',
            name='schema',
            field=json_field.fields.JSONField(blank=True, default=dict, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='freeze',
            name='schema',
            field=json_field.fields.JSONField(blank=True, default=dict, help_text='Enter a valid JSON object'),
        ),
    ]

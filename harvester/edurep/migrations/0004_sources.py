# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-28 15:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pol_harvester', '0012_optional_schema'),
        ('edurep', '0003_auto_20190214_1158'),
    ]

    operations = [
        migrations.CreateModel(
            name='EdurepHarvest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_after', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('stage', models.CharField(choices=[('Basic', 'Basic'), ('Complete', 'Complete'), ('New', 'New'), ('Video', 'Video')], default='New', max_length=50)),
                ('freeze', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pol_harvester.Freeze')),
            ],
        ),
        migrations.CreateModel(
            name='EdurepSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('query', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('freezes', models.ManyToManyField(through='edurep.EdurepHarvest', to='pol_harvester.Freeze')),
            ],
        ),
        migrations.AddField(
            model_name='edurepharvest',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edurep.EdurepSource'),
        ),
    ]

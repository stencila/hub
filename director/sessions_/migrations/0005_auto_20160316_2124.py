# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-16 21:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sessions_', '0004_auto_20160124_0931'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='network',
            field=models.IntegerField(blank=True, default=-1, help_text='Network limit for this session. -1 = unlimited', null=True),
        ),
        migrations.AddField(
            model_name='sessiontype',
            name='lifetime',
            field=models.IntegerField(default=-1, help_text='Minutes before the session is terminated. -1 = infinite.'),
        ),
        migrations.AddField(
            model_name='sessiontype',
            name='number',
            field=models.IntegerField(default=-1, help_text='Maximum number of this session type that can be running at one time. -1 = infinite.'),
        ),
        migrations.AddField(
            model_name='sessiontype',
            name='rank',
            field=models.IntegerField(default=1, help_text='Nominal rank of session type (higher ~ more powerful)'),
        ),
        migrations.AlterField(
            model_name='sessiontype',
            name='network',
            field=models.FloatField(default=0, help_text='Gigabytes (GB) of network transfer allocated to the session.'),
        ),
        migrations.AlterField(
            model_name='sessiontype',
            name='timeout',
            field=models.IntegerField(default=60, help_text='Minutes of inactivity before the session is terminated'),
        ),
    ]

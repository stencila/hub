# Generated by Django 2.0.8 on 2018-09-27 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_auto_20180913_0723'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='session',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='session',
            name='last_check',
            field=models.DateTimeField(blank=True, help_text='The last time the status of this Session was checked', null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='started',
            field=models.DateTimeField(blank=True, help_text='DateTime this Session was started.', null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='stopped',
            field=models.DateTimeField(blank=True, help_text='DateTime this Session was stopped (or that we detected it had stopped).', null=True),
        ),
    ]
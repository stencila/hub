# Generated by Django 3.1 on 2020-09-03 06:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_anonuser'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jobs', '0006_auto_20200806_0605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='anon_users',
            field=models.ManyToManyField(blank=True, help_text='Anonymous users who have created or connected to the job.', to='users.AnonUser'),
        ),
        migrations.AlterField(
            model_name='job',
            name='began',
            field=models.DateTimeField(blank=True, help_text='The time the job began.', null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='ended',
            field=models.DateTimeField(blank=True, help_text='The time the job ended.', null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='users',
            field=models.ManyToManyField(blank=True, help_text='Users who have created or connected to the job; not necessarily currently connected.', to=settings.AUTH_USER_MODEL),
        ),
    ]

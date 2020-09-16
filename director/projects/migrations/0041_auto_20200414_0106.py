# Generated by Django 2.2.12 on 2020-04-14 01:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0040_auto_20200409_0040'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, help_text='The time the source was created.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='source',
            name='creator',
            field=models.ForeignKey(blank=True, help_text='The user who created the source.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sources_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='projectevent',
            name='event_type',
            field=models.TextField(choices=[('SOURCE_PULL', 'SOURCE_PULL'), ('SNAPSHOT', 'SNAPSHOT'), ('CONVERT', 'CONVERT')]),
        ),
        migrations.AlterField(
            model_name='source',
            name='updated',
            field=models.DateTimeField(auto_now=True, help_text='The time the source was last changed'),
        ),
    ]
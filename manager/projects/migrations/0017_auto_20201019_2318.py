# Generated by Django 3.1.2 on 2020-10-19 23:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0009_auto_20201019_2318'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0016_auto_20201016_0326'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='subscription',
            field=models.JSONField(blank=True, help_text='Information from the source provider (e.g. Github, Google) when a watch subscription was created.', null=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='jobs',
            field=models.ManyToManyField(help_text='Jobs associated with this source. e.g. pull, push or convert jobs.', to='jobs.Job'),
        ),
        migrations.CreateModel(
            name='ProjectEvent',
            fields=[
                ('id', models.BigAutoField(help_text='Id of the event.', primary_key=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True, help_text='Time of the event.')),
                ('data', models.JSONField(help_text='Data associated with the event.')),
                ('project', models.ForeignKey(help_text='Project to which the event applies.', on_delete=django.db.models.deletion.CASCADE, related_name='events', to='projects.project')),
                ('source', models.ForeignKey(blank=True, help_text='Source associated with the event.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='projects.source')),
                ('user', models.ForeignKey(blank=True, help_text='User associated with the event.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

# Generated by Django 3.1.3 on 2020-11-12 23:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0019_googlesheetssource'),
    ]

    operations = [
        migrations.CreateModel(
            name='Doi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doi', models.CharField(help_text='The DOI string including both prefix and suffix e.g. 10.47704/stencila.54321', max_length=128)),
                ('url', models.URLField(help_text='The URL of the resource that this DOI is points to.')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date-time the DOI was created.')),
                ('deposited', models.DateField(blank=True, help_text='Date-time that the registration request was sent to the registrar.', null=True)),
                ('registered', models.DateField(blank=True, help_text='Date-time that a successful registration response was received from the registrar. If `deposited` is not null and this is null it implies that the registration was unsuccessful.', null=True)),
                ('request', models.JSONField(blank=True, help_text='JSON serialization of the request sent to the registrar.', null=True)),
                ('response', models.JSONField(blank=True, help_text='JSON serialization of the response received from the registrar.', null=True)),
                ('creator', models.ForeignKey(blank=True, help_text='The user who created the DOI.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dois_created', to=settings.AUTH_USER_MODEL)),
                ('node', models.ForeignKey(blank=True, help_text='The node that the DOI points to. Most Stencila DOIs point to a CreativeWork node of some type e.g. a Article, a Review, a Dataset.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dois', to='projects.node')),
            ],
        ),
    ]

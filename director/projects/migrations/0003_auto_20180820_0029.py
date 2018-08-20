# Generated by Django 2.0.8 on 2018-08-20 00:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import projects.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('checkouts', '0006_auto_20180723_1614'),
        ('projects', '0002_auto_20180723_0004_squashed_0004_auto_20180723_1708'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, help_text='Address of project e.g. github://org/repo/folder', max_length=1024)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='FilesSourceFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='unnamed', help_text='Name of the file (a path relative to the project root)', max_length=1024)),
                ('size', models.IntegerField(blank=True, help_text='Size of the file in bytes', null=True)),
                ('file', models.FileField(blank=True, help_text='The actual file stored', upload_to=projects.models.files_source_file_path)),
                ('updated', models.DateTimeField(auto_now=True, help_text='Time this model instance was last updated')),
                ('modified', models.DateTimeField(blank=True, help_text='Time the file was last modified', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceLimit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField(blank=True, help_text='Optional long description about the ResourceLimit', null=True)),
                ('memory', models.FloatField(default=1, help_text='Gigabytes (GB) of memory allocated')),
                ('cpu', models.FloatField(default=1, help_text='CPU shares (out of 100 per CPU) allocated')),
                ('network', models.FloatField(blank=True, help_text='Gigabytes (GB) of network transfer allocated. null = unlimited', null=True)),
                ('lifetime', models.IntegerField(blank=True, help_text='Minutes before the session is terminated. null = unlimited', null=True)),
                ('timeout', models.IntegerField(default=60, help_text='Minutes of inactivity before the session is terminated')),
                ('owner', models.ForeignKey(help_text='User who owns the SessionTemplate', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='session_templates', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(help_text='URL for API access to administrate this Session')),
                ('started', models.DateTimeField(help_text='DateTime this Session was started', null=True)),
                ('stopped', models.DateTimeField(help_text='DateTime this Session was stopped (or that we detected it had stopped)', null=True)),
                ('last_check', models.DateTimeField(help_text='The last time the status of this Session was checked', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='filesproject',
            name='project_ptr',
        ),
        migrations.RemoveField(
            model_name='filesprojectfile',
            name='project',
        ),
        migrations.AlterModelOptions(
            name='project',
            options={},
        ),
        migrations.RemoveField(
            model_name='project',
            name='address',
        ),
        migrations.RemoveField(
            model_name='project',
            name='polymorphic_ctype',
        ),
        migrations.AddField(
            model_name='project',
            name='key',
            field=models.TextField(blank=True, help_text='Key required to create Sessions in this SessionGroup', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='max_concurrent',
            field=models.IntegerField(help_text='Maximum number of sessions allowed to run at one time for this SessionGroup (null = unlimited)', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='max_queue',
            field=models.IntegerField(help_text='Maximum number of users waiting for a new Session to be created in this Session Group (null = unlimited)', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='max_sessions',
            field=models.IntegerField(help_text='Maximum total number of sessions that can be created in this SessionGroup (null = unlimited)', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='token',
            field=models.TextField(default='', help_text='A token to publicly identify the SessionGroup (in URLs etc)', unique=True),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='FilesSource',
            fields=[
                ('datasource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='projects.DataSource')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('projects.datasource',),
        ),
        migrations.DeleteModel(
            name='FilesProject',
        ),
        migrations.DeleteModel(
            name='FilesProjectFile',
        ),
        migrations.AddField(
            model_name='session',
            name='project',
            field=models.ForeignKey(help_text='The Project that this Session belongs to.', on_delete=django.db.models.deletion.PROTECT, related_name='sessions', to='projects.Project'),
        ),
        migrations.AddField(
            model_name='datasource',
            name='creator',
            field=models.ForeignKey(help_text='User who created this data source', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sources', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='datasource',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_projects.datasource_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='datasource',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sources', to='projects.Project'),
        ),
        migrations.AddField(
            model_name='project',
            name='resource_limit',
            field=models.ForeignKey(help_text='The SessionTemplate that defines resources for new sessions in this group.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='session_groups', to='projects.ResourceLimit'),
        ),
        migrations.AddField(
            model_name='filessourcefile',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='projects.FilesSource'),
        ),
    ]

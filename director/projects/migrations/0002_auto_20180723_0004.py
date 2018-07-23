# Generated by Django 2.0.7 on 2018-07-23 00:04

from django.db import migrations, models
import projects.models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='filesprojectfile',
            name='modified',
            field=models.DateTimeField(blank=True, help_text='Time the file was last modified', null=True),
        ),
        migrations.AddField(
            model_name='filesprojectfile',
            name='name',
            field=models.CharField(default='unnamed', help_text='Name of the file (a path relative to the project root)', max_length=1024),
        ),
        migrations.AddField(
            model_name='filesprojectfile',
            name='size',
            field=models.IntegerField(blank=True, help_text='Size of the file in bytes', null=True),
        ),
        migrations.AddField(
            model_name='filesprojectfile',
            name='updated',
            field=models.DateTimeField(auto_now=True, help_text='Time this model instance was last updated'),
        ),
        migrations.AlterField(
            model_name='filesprojectfile',
            name='file',
            field=models.FileField(blank=True, help_text='The actual file stored', upload_to=projects.models.files_project_file_path),
        ),
        migrations.AlterUniqueTogether(
            name='filesprojectfile',
            unique_together={('project', 'name')},
        ),
    ]

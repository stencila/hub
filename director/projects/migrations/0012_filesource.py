from django.db import migrations, models
import django.db.models.deletion
import projects.source_models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_auto_20180927_2230'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileSource',
            fields=[
                ('source_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='projects.Source')),
                ('size', models.IntegerField(blank=True, help_text='Size of the file in bytes', null=True)),
                ('file', models.FileField(blank=True, help_text='The actual file stored', upload_to=projects.source_models.files_source_file_path)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('projects.source',),
        ),
        migrations.AddField(
            model_name='source',
            name='path',
            field=models.TextField(default='.', help_text='The path that the file or directory from the source is mapped to in the project'),
        ),
        migrations.AddField(
            model_name='source',
            name='updated',
            field=models.DateTimeField(auto_now=True, help_text='Time this model instance was last updated'),
        ),
        migrations.DeleteModel(
            name='FilesSource',
        ),
        migrations.DeleteModel(
            name='FilesSourceFile',
        ),
    ]

# Generated by Django 3.0.7 on 2020-06-29 07:28

from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import projects.models.sources


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='The time the project was created.')),
                ('name', models.SlugField(help_text='Name of the project. Lowercase only and unique for the account. Will be used in URLS e.g. https://hub.stenci.la/awesome-org/great-project.')),
                ('title', models.CharField(blank=True, help_text='Title of the project to display in its profile.', max_length=256, null=True)),
                ('public', models.BooleanField(default=True, help_text='Should the project be publicly visible?')),
                ('description', models.TextField(blank=True, help_text='Brief description of the project.', null=True)),
                ('theme', models.TextField(blank=True, help_text='The name of the theme to use as the default when generating content for this project.', null=True)),
                ('account', models.ForeignKey(help_text='Account that the project belongs to.', on_delete=django.db.models.deletion.PROTECT, related_name='projects', to='accounts.Account')),
                ('creator', models.ForeignKey(help_text='The user who created the project.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects_created', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(help_text='The address of the source. e.g. github://org/repo/subpath')),
                ('url', models.URLField(help_text='The URL of the source. Provided for users to be able to navigate to the external source.')),
                ('path', models.TextField(help_text='The path that the source is mapped to in the project.')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='The time the source was created.')),
                ('updated', models.DateTimeField(auto_now=True, help_text='The time the source was last changed.')),
                ('creator', models.ForeignKey(blank=True, help_text='The user who created the source.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sources_created', to=settings.AUTH_USER_MODEL)),
                ('jobs', models.ManyToManyField(help_text='Jobs associated with this source. e.g. pull, push or convert jobs', to='jobs.Job')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_projects.source_set+', to='contenttypes.ContentType')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=projects.models.sources.NON_POLYMORPHIC_CASCADE, related_name='sources', to='projects.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ElifeSource',
            fields=[
                ('source_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='projects.Source')),
                ('article', models.IntegerField(help_text='The article number.')),
                ('version', models.IntegerField(blank=True, help_text='The article version. If blank, defaults to the latest.', null=True)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('projects.source',),
        ),
        migrations.CreateModel(
            name='GithubSource',
            fields=[
                ('source_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='projects.Source')),
                ('repo', models.CharField(help_text='The Github repository identifier i.e. org/repo', max_length=512)),
                ('subpath', models.CharField(blank=True, help_text='Path to file or folder within the repository', max_length=1024, null=True)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('projects.source',),
        ),
        migrations.CreateModel(
            name='GoogleDocsSource',
            fields=[
                ('source_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='projects.Source')),
                ('doc_id', models.TextField(help_text='The id of the document e.g. 1iNeKTanIcW_92Hmc8qxMkrW2jPrvwjHuANju2hkaYkA')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('projects.source',),
        ),
        migrations.CreateModel(
            name='GoogleDriveSource',
            fields=[
                ('source_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='projects.Source')),
                ('folder_id', models.TextField(help_text="Google's ID of the folder.")),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('projects.source',),
        ),
        migrations.CreateModel(
            name='PlosSource',
            fields=[
                ('source_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='projects.Source')),
                ('article', models.TextField(help_text='The article DOI.')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('projects.source',),
        ),
        migrations.CreateModel(
            name='UploadSource',
            fields=[
                ('source_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='projects.Source')),
                ('file', models.FileField(help_text='The uploaded file.', storage=django.core.files.storage.FileSystemStorage(location='/home/nokome/stencila/source/hub/manager/media/private'), upload_to=projects.models.sources.upload_source_path)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('projects.source',),
        ),
        migrations.CreateModel(
            name='UrlSource',
            fields=[
                ('source_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='projects.Source')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('projects.source',),
        ),
        migrations.CreateModel(
            name='Snapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='The time the snapshot was created.')),
                ('creator', models.ForeignKey(help_text='The user who created the snapshot.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='snapshots_created', to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(blank=True, help_text='The job that created the snapshot', null=True, on_delete=django.db.models.deletion.PROTECT, to='jobs.Job')),
                ('project', models.ForeignKey(help_text='The project that the snapshot is for.', on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='projects.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('READER', 'Reader'), ('REVIEWER', 'Reviewer'), ('EDITOR', 'Editor'), ('AUTHOR', 'Author'), ('MANAGER', 'Manager'), ('OWNER', 'Owner')], help_text='Role the user or team has within the project.', max_length=32)),
                ('project', models.ForeignKey(help_text='Project to which the user or team is being given access to.', on_delete=django.db.models.deletion.CASCADE, related_name='agents', to='projects.Project')),
                ('team', models.ForeignKey(blank=True, help_text='A team given access to the project.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='accounts.AccountTeam')),
                ('user', models.ForeignKey(blank=True, help_text='A user given access to the project.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.TextField(db_index=True, help_text='The path of the file within the project.')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='The time the file info was created.')),
                ('updated', models.DateTimeField(auto_now=True, help_text='The time the file info was update.')),
                ('modified', models.DateTimeField(blank=True, help_text='The file modification time.', null=True)),
                ('size', models.PositiveIntegerField(blank=True, help_text='The size of the file in bytes', null=True)),
                ('mimetype', models.CharField(blank=True, help_text='The mimetype of the file.', max_length=512, null=True)),
                ('encoding', models.CharField(blank=True, help_text='The encoding of the file e.g. gzip', max_length=512, null=True)),
                ('dependencies', models.ManyToManyField(help_text='Files that this file was derived from.', related_name='dependants', to='projects.File')),
                ('job', models.ForeignKey(blank=True, help_text='The job that created the file e.g. a source pull or file conversion.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='jobs.Job')),
                ('project', models.ForeignKey(help_text='The project that the file is associated with.', on_delete=django.db.models.deletion.CASCADE, related_name='files', to='projects.Project')),
                ('source', models.ForeignKey(blank=True, help_text='The source from which the file came (if any). If the source is removed from the project, so will the files.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='projects.Source')),
            ],
        ),
        migrations.AddConstraint(
            model_name='source',
            constraint=models.UniqueConstraint(fields=('project', 'address'), name='source_unique_project_address'),
        ),
        migrations.AddConstraint(
            model_name='projectagent',
            constraint=models.UniqueConstraint(fields=('project', 'user'), name='projectagent_unique_project_user'),
        ),
        migrations.AddConstraint(
            model_name='projectagent',
            constraint=models.UniqueConstraint(fields=('project', 'team'), name='projectagent_unique_project_team'),
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.UniqueConstraint(fields=('account', 'name'), name='project_unique_account_name'),
        ),
        migrations.AddConstraint(
            model_name='file',
            constraint=models.UniqueConstraint(fields=('project', 'path'), name='file_unique_project_path'),
        ),
    ]

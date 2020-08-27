# Generated by Django 3.0.8 on 2020-07-08 22:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(default=users.models.generate_invite_key, help_text='The key for the invite.', max_length=64, unique=True)),
                ('email', models.EmailField(help_text='The email address of the person you are inviting.', max_length=2048)),
                ('message', models.TextField(blank=True, help_text='An optional message to send to the invitee.', null=True)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='When the invite was created.')),
                ('sent', models.DateTimeField(blank=True, help_text='When the invite was sent.', null=True)),
                ('accepted', models.BooleanField(default=False, help_text='Whether the invite has been accepted. Will only be true if the user has clicked on the invitation AND authenticated.')),
                ('completed', models.DateTimeField(blank=True, help_text='When the invite action was completed', null=True)),
                ('action', models.CharField(blank=True, choices=[('join_account', 'Join account'), ('join_team', 'Join team'), ('join_project', 'Join project'), ('take_tour', 'Take tour')], help_text='The action to perform when the invitee signs up.', max_length=64, null=True)),
                ('subject_id', models.IntegerField(blank=True, help_text='The id of the target of the action.', null=True)),
                ('arguments', models.JSONField(blank=True, help_text='Any additional arguments to pass to the action.', null=True)),
                ('inviter', models.ForeignKey(blank=True, help_text='The user who created the invite.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invites', to=settings.AUTH_USER_MODEL)),
                ('subject_type', models.ForeignKey(blank=True, help_text='The type of the target of the action. e.g Team, Account', null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The human/computer readable name.', max_length=100, unique=True, verbose_name='Name')),
                ('everyone', models.NullBooleanField(help_text='Flip this flag on (Yes) or off (No) for everyone, overriding all other settings. Leave as Unknown to use normally.', verbose_name='Everyone')),
                ('percent', models.DecimalField(blank=True, decimal_places=1, help_text='A number between 0.0 and 99.9 to indicate a percentage of users for whom this flag will be active.', max_digits=3, null=True, verbose_name='Percent')),
                ('testing', models.BooleanField(default=False, help_text='Allow this flag to be set for a session for user testing', verbose_name='Testing')),
                ('superusers', models.BooleanField(default=True, help_text='Flag always active for superusers?', verbose_name='Superusers')),
                ('staff', models.BooleanField(default=False, help_text='Flag always active for staff?', verbose_name='Staff')),
                ('authenticated', models.BooleanField(default=False, help_text='Flag always active for authenticated users?', verbose_name='Authenticated')),
                ('languages', models.TextField(blank=True, default='', help_text='Activate this flag for users with one of these languages (comma-separated list)', verbose_name='Languages')),
                ('rollout', models.BooleanField(default=False, help_text='Activate roll-out mode?', verbose_name='Rollout')),
                ('note', models.TextField(blank=True, help_text='Note where this Flag is used.', verbose_name='Note')),
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, help_text='Date when this Flag was created.', verbose_name='Created')),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, help_text='Date when this Flag was last modified.', verbose_name='Modified')),
                ('groups', models.ManyToManyField(blank=True, help_text='Activate this flag for these user groups.', to='auth.Group', verbose_name='Groups')),
                ('users', models.ManyToManyField(blank=True, help_text='Activate this flag for these users.', to=settings.AUTH_USER_MODEL, verbose_name='Users')),
            ],
            options={
                'verbose_name': 'Flag',
                'verbose_name_plural': 'Flags',
                'abstract': False,
            },
        ),
    ]

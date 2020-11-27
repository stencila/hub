# Generated by Django 3.1.3 on 2020-11-27 06:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0005_auto_20201127_0625'),
        ('jobs', '0011_auto_20201127_0625'),
        ('projects', '0021_auto_20201119_0526'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='The time the review was created.')),
                ('updated', models.DateTimeField(auto_now=True, help_text='The time the review was last updated.')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('INVITED', 'Invited'), ('ACCEPTED', 'Accepted'), ('CANCELLED', 'Cancelled'), ('COMPLETED', 'Completed'), ('EXTRACTING', 'Retrieval in progress'), ('EXTRACTED', 'Retrieved'), ('FAILED', 'Retrieval failed')], default='PENDING', help_text='The status of the review.', max_length=16)),
                ('reviewer_email', models.EmailField(blank=True, help_text='The email address of the reviewer.', max_length=254, null=True)),
                ('reviewer_name', models.CharField(blank=True, help_text='The name of the reviewer.', max_length=128, null=True)),
                ('invite_message', models.TextField(blank=True, help_text='The message to send to the reviewer in the invitation.', null=True)),
                ('review_date', models.DateTimeField(blank=True, help_text="The date of the review e.g it's `datePublished`.", null=True)),
                ('review_comments', models.IntegerField(blank=True, help_text='The number of comments that the review has.', null=True)),
                ('creator', models.ForeignKey(blank=True, help_text='The user who created the review.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviews_created', to=settings.AUTH_USER_MODEL)),
                ('invite', models.ForeignKey(blank=True, help_text='The invite sent to the reviewer.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.invite')),
                ('job', models.ForeignKey(blank=True, help_text='The job that extracted the review from the source.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reviews', to='jobs.job')),
                ('project', models.ForeignKey(help_text='The project that the review is for.', on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='projects.project')),
                ('review', models.ForeignKey(blank=True, help_text='The node, of type `Review`, representing the actual review.', null=True, on_delete=django.db.models.deletion.PROTECT, to='projects.node')),
                ('reviewer', models.ForeignKey(blank=True, help_text='The user who authored the review.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviews_authored', to=settings.AUTH_USER_MODEL)),
                ('source', models.ForeignKey(blank=True, help_text='The source for this review.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviews', to='projects.source')),
                ('subject', models.ForeignKey(blank=True, help_text='The node, usually a `CreativeWork`, that is the subject of the review.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reviews', to='projects.node')),
            ],
        ),
    ]

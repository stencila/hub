# Generated by Django 3.1.7 on 2021-03-28 23:41

from django.db import migrations, models
import django.db.models.deletion
import manager.storage
import projects.models.sources


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0030_auto_20210315_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='source',
            field=models.ForeignKey(blank=True, help_text='The source this node is associated with (if any).', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='nodes', to='projects.source'),
        ),
        migrations.AlterField(
            model_name='node',
            name='project',
            field=models.ForeignKey(blank=True, help_text='The project this node is associated with (if any).', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='nodes', to='projects.project'),
        )
    ]
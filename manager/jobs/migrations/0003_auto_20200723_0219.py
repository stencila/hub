# Generated by Django 3.0.8 on 2020-07-23 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20200708_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='id',
            field=models.BigAutoField(help_text='An autoincrementing integer to allow selecting jobs in the order they were created.', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='job',
            name='method',
            field=models.CharField(choices=[('parallel', 'parallel'), ('series', 'series'), ('chain', 'chain'), ('clean', 'clean'), ('archive', 'archive'), ('pull', 'pull'), ('push', 'push'), ('decode', 'decode'), ('encode', 'encode'), ('convert', 'convert'), ('compile', 'compile'), ('build', 'build'), ('execute', 'execute'), ('session', 'session'), ('sleep', 'sleep')], help_text='The job method.', max_length=32),
        ),
    ]

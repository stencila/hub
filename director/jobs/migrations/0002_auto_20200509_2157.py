# Generated by Django 2.2.12 on 2020-05-09 21:57

from django.db import migrations, models
import django.db.models.deletion
import jsonfallback.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the queue.', max_length=512)),
                ('priority', models.IntegerField(default=0, help_text='The relative priority of jobs placed on the queue.')),
                ('untrusted', models.BooleanField(default=False, help_text='Whether or not the queue should be sent jobs which run untrusted code.')),
                ('interrupt', models.BooleanField(default=False, help_text='Whether or not the queue should be sent jobs which can not be interupted.False (default): jobs should not be interrupted')),
                ('zone', models.ForeignKey(blank=True, help_text='The zone this job is associated with.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='jobs.Zone')),
            ],
        ),
        migrations.CreateModel(
            name='WorkerHeartbeat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(help_text='The time of the heartbeat.')),
                ('clock', models.IntegerField(help_text="The tick number of the worker's monotonic clock")),
                ('active', models.IntegerField(help_text='The number of active jobs on the worker.')),
                ('processed', models.IntegerField(help_text='The number of jobs that have been processed by the worker.')),
                ('load', jsonfallback.fields.FallbackJSONField(help_text='An array of the system load over the last 1, 5 and 15 minutes. From os.getloadavg().')),
            ],
        ),
        migrations.RemoveField(
            model_name='job',
            name='zone',
        ),
        migrations.RemoveField(
            model_name='worker',
            name='zone',
        ),
        migrations.AddField(
            model_name='worker',
            name='details',
            field=jsonfallback.fields.FallbackJSONField(blank=True, help_text='Details about the worker including queues and statsSee https://docs.celeryproject.org/en/stable/userguide/workers.html#statistics', null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='queue',
            field=models.ForeignKey(blank=True, help_text='The queue that this job was routed to', null=True, on_delete=django.db.models.deletion.SET_NULL, to='jobs.Queue'),
        ),
        migrations.DeleteModel(
            name='WorkerStatus',
        ),
        migrations.AddField(
            model_name='workerheartbeat',
            name='worker',
            field=models.ForeignKey(help_text='The worker that the heartbeat is for.', on_delete=django.db.models.deletion.CASCADE, related_name='heartbeats', to='jobs.Worker'),
        ),
        migrations.AddField(
            model_name='worker',
            name='queues',
            field=models.ManyToManyField(help_text='The queues that this worker is listening to.', related_name='workers', to='jobs.Queue'),
        ),
    ]

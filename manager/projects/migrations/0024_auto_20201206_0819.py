# Generated by Django 3.1.4 on 2020-12-06 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_auto_20201202_0349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('REQUESTED', 'Requested'), ('CANCELLED', 'Cancelled'), ('ACCEPTED', 'Accepted'), ('DECLINED', 'Declined'), ('COMPLETED', 'Completed'), ('EXTRACTING', 'Retrieval in progress'), ('EXTRACTED', 'Retrieved'), ('FAILED', 'Retrieval failed'), ('REGISTERED', 'Registered')], default='PENDING', help_text='The status of the review.', max_length=16),
        ),
    ]

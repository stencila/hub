# Generated by Django 3.0.8 on 2020-07-21 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20200720_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounttier',
            name='active',
            field=models.BooleanField(default=True, help_text='Is the tier active i.e. should be displayed to users.'),
        ),
        migrations.AlterField(
            model_name='accounttier',
            name='name',
            field=models.CharField(help_text='The name of the tier.', max_length=64, unique=True),
        ),
    ]

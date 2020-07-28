# Generated by Django 2.2.7 on 2019-11-26 19:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djstripe', '0004_2_1'),
        ('accounts', '0008_auto_20191114_0032'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductResourceAllowance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allowances', models.TextField(help_text='Allowances granted in JSON format.')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='resource_allowance', to='djstripe.Product')),
            ],
        ),
    ]
# Generated by Django 3.1.3 on 2020-11-19 05:26

from django.db import migrations, models
import projects.models.nodes


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0020_auto_20201116_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='key',
            field=models.CharField(default=projects.models.nodes.generate_node_key, help_text='A unique, and very difficult to guess, key to access this node if it is not public.', max_length=64, unique=True),
        ),
    ]

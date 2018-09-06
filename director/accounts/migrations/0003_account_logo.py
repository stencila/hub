from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20180905_2054'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='logo',
            field=models.ImageField(blank=True, help_text='A logo for the acccount', null=True, upload_to=''),
        ),
    ]

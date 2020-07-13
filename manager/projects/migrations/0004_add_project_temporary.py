from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

def temp_account(apps, *args):
    """
    Create a temp account that will own temporary projects.
    """
    Account = apps.get_model("accounts", "Account")
    Account.objects.create(name="temp", display_name="Temporary projects")


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0003_auto_20200712_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='temporary',
            field=models.BooleanField(default=False, help_text='Is the project temporary?'),
        ),
        migrations.RunPython(temp_account),
        migrations.AlterField(
            model_name='project',
            name='creator',
            field=models.ForeignKey(blank=True, help_text='The user who created the project.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='project',
            name='public',
            field=models.BooleanField(default=True, help_text='Is the project publicly visible?'),
        ),
    ]

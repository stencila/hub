from django.db import migrations, models

def create_flags(apps, schema_editor):
    Flag = apps.get_model('users', 'Flag')
    Flag.objects.create(
        name = "product_messages",
        label = "Support messages",
        note = "We use Intercom to provide in-app support via chat messages and notifications.",
        superusers = False,
        default = "on",
        settable = True
    )
    Flag.objects.create(
        name = "product_tours",
        label = "Product tours",
        note = "We use UserFlow to provide in-app product tours and onboarding checklists.",
        superusers = False,
        default = "on",
        settable = True
    )
    Flag.objects.create(
        name = "product_analytics",
        label = "Product analytics",
        note = "We use PostHog to collect analytics on how users use our products.",
        superusers = False,
        default = "on",
        settable = True,
    )
    Flag.objects.create(
        name = "crash_monitoring",
        label = "Crash monitoring",
        note = "We use Sentry for application monitoring and error reporting.",
        superusers = False,
        default = "on",
        settable = True
    )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20201005_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='flag',
            name='label',
            field=models.CharField(help_text='A label for the feature to display to users.', max_length=128),
        ),
        migrations.AddField(
            model_name='flag',
            name='default',
            field=models.CharField(choices=[('on', 'On'), ('off', 'Off')], default='on', help_text='If the default is "on" then when the flag is active, the feature should be considered "off" and vice versa.', max_length=3),
        ),
        migrations.AddField(
            model_name='flag',
            name='settable',
            field=models.BooleanField(default=False, help_text='User can turn this flag on/off for themselves.'),
        ),
        migrations.RunPython(create_flags),
    ]

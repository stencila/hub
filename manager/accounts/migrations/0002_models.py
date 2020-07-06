from django.db import migrations
from django.contrib.auth.hashers import make_password


def initial_models(apps, *args):
    """
    An initial data migration to create the necessary account related models.
    """

    # Need at least one account tier for accounts to belong to
    AccountTier = apps.get_model("accounts", "AccountTier")
    one = AccountTier.objects.create()

    # Need a Stencila account to own the default job queue etc
    Account = apps.get_model("accounts", "Account")
    stencila = Account.objects.create(name="stencila", display_name="Stencila", tier=three)

    # A staff user is needed for use by internal services
    # e.g. for the `overseer` service to authenticate to post job and worker updates
    User = apps.get_model("auth", "User")
    stencibot = User.objects.create(
        username="stencibot",
        password=make_password("stencibot"),
        is_staff=True,
        is_active=True,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(initial_models),
    ]

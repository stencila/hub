from django.db import migrations


def initial_models(apps, *args):
    """
    An initial data migration to create the necessary account related models.
    """

    # Need at least one account tier for accounts to belong to
    AccountTier = apps.get_model("accounts", "AccountTier")
    one = AccountTier.objects.create()

    # Need a Stencila account to own the default job queue etc
    Account = apps.get_model("accounts", "Account")
    stencila = Account.objects.create(name="stencila", display_name="Stencila")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(initial_models),
    ]

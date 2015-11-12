# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create(apps, schema_editor):
    AccountType = apps.get_model('accounts', 'AccountType')
    Account = apps.get_model('accounts', 'Account')

    community = AccountType.objects.create(name='community')
    AccountType.objects.create(name='bronze')
    AccountType.objects.create(name='silver')
    AccountType.objects.create(name='gold')
    platinum = AccountType.objects.create(name='platinum')

    Account.objects.create(
        name="Community",
        type=community
    )
    Account.objects.create(
        name="Stencila",
        type=platinum
    )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create)
    ]

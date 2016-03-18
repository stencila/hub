# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_user_any(apps, schema_editor):
    '''
    Create an "any" user with no password or other details, whose
    sole purpose is to be used in access keys.
    '''
    from django.contrib.auth.models import User
    try:
        User.objects.get(username='any')
    except User.DoesNotExist:
        User.objects.create_user(username='any')


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20160129_1752'),
    ]

    operations = [
        migrations.RunPython(create_user_any)
    ]

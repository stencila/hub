# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_site(apps, schema_editor):
    '''
    There must be at least one site for allauth
    '''
    from django.contrib.sites.models import Site
    site, created = Site.objects.get_or_create(pk=1)
    site.domain = 'stenci.la'
    site.name = 'stenci.la'
    site.save()


def create_socialapps(apps, schema_editor):
    '''
    Each allauth provider needs to have a model instance
    linked to the site
    '''
    from allauth.socialaccount.models import SocialApp

    for provider, name in (
        ('facebook', 'Facebook'),
        ('github', 'Github'),
        ('google', 'Google'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
    ):
        app = SocialApp.objects.create(
            provider=provider,
            name=name,
            client_id='client-id-to-be-provided',
            secret='secret-to-be-provided',
        )
        app.sites.add(1)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_site),
        migrations.RunPython(create_socialapps)
    ]

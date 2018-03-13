from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import json
import os
import simplecrypt
import warnings


def run():
    # There must be at least one site
    site, created = Site.objects.get_or_create(pk=1)
    site.domain = 'stenci.la'
    site.name = 'stenci.la'
    site.save()

    # Get oauth client ids and secrets
    try:
        path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..',
            'secrets', 'director-allauth.json.enc'
        )
        pw = os.environ['STENCILA_DEVPASS']
        with open(path, 'rb') as file:
            data = simplecrypt.decrypt(pw, file.read())
            secrets = json.loads(data.decode('utf-8'))
    except Exception as exc:
        warnings.warn('Warning, unable to open allauth SocialApp secrets:', RuntimeWarning)
        print(exc)
        secrets = {}

    # Create `SocialApp` objects for each provider
    for provider in 'facebook', 'github', 'google', 'linkedin_oauth2', 'orcid', 'twitter':
        provider_secrets = secrets.get(provider, {
            'client_id': 'missing-client-id',
            'secret': 'missing-secret'
        })
        app = SocialApp.objects.create(
            provider=provider,
            name=provider,
            client_id=provider_secrets['client_id'],
            secret=provider_secrets['secret'],
        )
        app.sites.add(1)

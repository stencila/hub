from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings
import json
import os
import warnings


def run():
    # There must be at least one site
    site, created = Site.objects.get_or_create(pk=1)
    site.domain = 'hub.stenci.la'
    site.name = 'hub.stenci.la'
    site.save()

    try:
        path = os.path.join(settings.SECRETS_DIR, 'director-allauth.json')
        with open(path) as file:
            providers = json.loads(file.read())
    except Exception:
        warnings.warn('Warning, unable to find allauth data', RuntimeWarning)
        providers = {
           'example.com': {
                'client_id': 'missing-client-id',
                'secret': 'missing-secret'
            }
        }

    # Create `SocialApp` objects for each provider
    for provider, secrets in providers.items():
        app = SocialApp.objects.create(
            provider=provider,
            name=provider,
            client_id=secrets['client_id'],
            secret=secrets['secret'],
        )
        app.sites.add(1)

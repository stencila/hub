'''
Creates a super user for using the admin interface during development.
'''
from django.conf import settings

def run():
    if settings.MODE == 'local':
        from django.contrib.auth.models import User
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            User.objects.create_superuser('admin', 'hub@stenci.la', 'insecure')
    else:
        raise Exception('Whaaaat! You trying to run this out of development mode! %s' % settings.MODE)

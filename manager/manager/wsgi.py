import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manager.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Prod")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()

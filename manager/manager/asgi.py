import os

os.environ.setdefault("DJANGO_CONFIGURATION", "Prod")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manager.settings")

from django.core.asgi import get_asgi_application  # noqa: E402

application = get_asgi_application()

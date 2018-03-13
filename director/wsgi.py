#!/usr/bin/python3
import os
import bjoern

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'director.config.prod')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Prod')

from configurations.wsgi import get_wsgi_application

wsgi_app = get_wsgi_application()

if __name__ == '__main__':
    bjoern.run(wsgi_app, '0.0.0.0', 8080, reuse_port=True)


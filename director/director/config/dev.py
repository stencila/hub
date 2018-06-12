import imp
import os
import sys
import traceback

from os.path import dirname

from configurations import values
from .common import Common, BASE_DIR, external_keys

SECRETS_DIR = os.path.join(dirname(BASE_DIR), "secrets")

class Dev(Common):

    DEBUG = True

    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'django_extensions'
    ]

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    @classmethod
    def setup(cls):
        super(Dev, cls).setup()
        filename = "director_dev_secrets.py"
        path = os.path.join(SECRETS_DIR, filename)
        try:
            dev_secrets = imp.load_source("dev_secrets", path)
        except ImportError as e:
            print("Could not import %s: %s" % (filename, e))
            return
        except FileNotFoundError as e:
            print("File %s not found" % path)
            return

        for key in external_keys:
            if not hasattr(cls, key) and hasattr(dev_secrets, key):
                setattr(cls, key, getattr(dev_secrets, key))

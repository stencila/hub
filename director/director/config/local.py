from configurations import values
from .common import Common

class Local(Common):

    JWT_SECRET = values.Value('not-a-secret')
    DEBUG = values.BooleanValue(True)

from configurations import values
from .common import Common

class Local(Common):

    DEBUG = values.BooleanValue(True)

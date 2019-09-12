# flake8: noqa F401
from django.contrib import admin

from stencila_open.models import Conversion, ConversionFeedback

admin.site.register(Conversion)
admin.site.register(ConversionFeedback)

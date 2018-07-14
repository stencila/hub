from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Checkout


@admin.register(Checkout)
class CheckoutAdmin(ModelAdmin):
    pass

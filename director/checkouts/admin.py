from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Checkout


@admin.register(Checkout)
class CheckoutAdmin(ModelAdmin):
    list_display = [
        '__str__', 'creator', 'created'
    ]

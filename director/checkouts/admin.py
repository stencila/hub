from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Checkout


@admin.register(Checkout)
class CheckoutAdmin(ModelAdmin):
    list_display = [
        'id', 'project', 'creator', 'status', 'created', 'saved', 'closed'
    ]
    list_select_related = (
        'creator',
        'project'
    )

from django.contrib import admin

from .models import Checkout, CheckoutEvent


class CheckoutEventInline(admin.TabularInline):
    model = CheckoutEvent
    readonly_fields = [
        'time', 'type', 'topic', 'message', 'data'
    ]


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'project', 'creator', 'status', 'created', 'saved', 'closed'
    ]
    list_select_related = [
        'creator',
        'project'
    ]
    inlines = [
        CheckoutEventInline
    ]


@admin.register(CheckoutEvent)
class CheckoutEventAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'checkout_id', 'time', 'type', 'topic'
    ]

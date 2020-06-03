from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Admin interface for accounts."""

    def is_personal(self, instance):
        """Field to display `is_personal` as a boolean."""
        return instance.is_personal

    is_personal.boolean = True
    is_personal.short_description = u"Personal"

    list_display = [
        "name",
        "creator",
        "created",
        "is_personal",
    ]
    list_select_related = ["creator"]

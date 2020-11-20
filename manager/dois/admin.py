from django.contrib import admin

from dois.models import Doi


@admin.register(Doi)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for DOIs."""

    list_display = [
        "doi",
        "url",
        "creator_id",
        "created",
        "deposited",
        "deposit_success",
        "registered",
        "registration_success",
    ]

    list_filter = [
        "created",
        "deposited",
        "deposit_success",
        "registered",
        "registration_success",
    ]

    readonly_fields = [
        "doi",
        "creator",
        "created",
        "deposited",
        "deposit_request",
        "deposit_response",
        "deposit_success",
        "registered",
        "registration_response",
        "registration_success",
    ]

    actions = ["register"]

    def register(self, request, queryset):
        """Register the selected DOIs."""
        for doi in queryset.all():
            doi.register()

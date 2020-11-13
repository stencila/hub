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
        "registered",
    ]
    list_filter = ["created", "deposited", "registered"]

    readonly_fields = [
        "doi",
        "creator",
        "created",
        "deposited",
        "registered",
        "request",
        "response",
    ]

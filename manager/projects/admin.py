from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for projects."""

    list_display = [
        "name",
        "creator",
        "created",
    ]
    list_select_related = ["creator"]

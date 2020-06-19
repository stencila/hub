from django.contrib import admin

from projects.models.projects import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for projects."""

    list_display = [
        "name",
        "creator",
        "created",
    ]
    list_select_related = ["creator"]

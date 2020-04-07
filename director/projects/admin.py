# flake8: noqa F401
from django.contrib import admin

from .project_admin import (
    ProjectAdmin,
    ProjectPermissionAdmin,
    ProjectRoleAdmin,
    ProjectAgentRoleAdmin,
)
from .session_admin import SessionAdmin, SessionParametersAdmin, SessionRequestAdmin
from .source_admin import SourceAdmin

from .models import Node


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ["key", "creator", "created", "project", "app", "host"]
    list_filter = ["app"]

    # Optimizations to reduce number of queries made.
    list_select_related = ["creator", "project"]
    show_full_result_count = False

    def get_queryset(self, request):
        """Get custom queryset that does not fetch the `json` field (which can be large)."""
        queryset = super().get_queryset(request)
        return queryset.defer("json")

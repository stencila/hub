from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)

from .project_admin import (
    ProjectAdmin,
    ProjectPermissionAdmin,
    ProjectRoleAdmin,
    ProjectAgentRoleAdmin,
)
from .session_admin import SessionAdmin, SessionParametersAdmin, SessionRequestAdmin

from projects.models import Node, Snapshot
from projects.source_models import (
    Source,
    FileSource,
    GithubSource,
    GoogleDocsSource,
    UrlSource,
)


@admin.register(Source)
class SourceParentAdmin(PolymorphicParentModelAdmin):
    base_model = Source
    child_models = (FileSource, GithubSource, GoogleDocsSource, UrlSource)

    list_display = ["id", "project_id", "path", "updated", "polymorphic_ctype"]
    list_select_related = ["polymorphic_ctype"]
    list_filter = [PolymorphicChildModelFilter]
    show_full_result_count = False


class SourceChildAdmin(PolymorphicChildModelAdmin):
    """Base admin class for all child models of Source."""


@admin.register(FileSource)
class FileSourceAdmin(SourceChildAdmin):
    base_model = FileSource
    show_in_index = True


@admin.register(GithubSource)
class GithubSourceAdmin(SourceChildAdmin):
    base_model = GithubSource
    show_in_index = True


@admin.register(GoogleDocsSource)
class GoogleDocsSourceAdmin(SourceChildAdmin):
    base_model = GoogleDocsSource
    show_in_index = True


@admin.register(UrlSource)
class UrlSourceAdmin(SourceChildAdmin):
    base_model = UrlSource
    show_in_index = True


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ["id", "key", "creator", "created", "project", "app", "host"]
    list_select_related = ["creator", "project"]
    list_filter = ["app"]
    show_full_result_count = False

    def get_queryset(self, request):
        """Get custom queryset that does not fetch the `json` field (which can be large)."""
        queryset = super().get_queryset(request)
        return queryset.defer("json")


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "project",
        "version_number",
        "tag",
        "creator",
        "created",
        "completed",
    ]
    list_select_related = ["creator", "project"]

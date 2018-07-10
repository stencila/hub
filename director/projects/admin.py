from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter
)

from .models import (
    Project,
    FilesProject, FilesProjectFile,
    GithubProject
)


@admin.register(Project)
class ProjectAdmin(PolymorphicParentModelAdmin):
    base_model = Project
    child_models = [
        FilesProject,
        GithubProject,
    ]
    list_filter = [
        PolymorphicChildModelFilter
    ]


class FilesProjectFileInline(admin.TabularInline):
    model = FilesProjectFile


@admin.register(FilesProject)
class FilesProjectAdmin(PolymorphicChildModelAdmin):
    base_model = FilesProject
    inlines = [
        FilesProjectFileInline
    ]


@admin.register(GithubProject)
class GithubProjectAdmin(PolymorphicChildModelAdmin):
    base_model = GithubProject

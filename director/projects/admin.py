from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter
)

from .models import (
    Project,
    FileProject, FileProjectFile,
    GithubProject
)


@admin.register(Project)
class ProjectAdmin(PolymorphicParentModelAdmin):
    base_model = Project
    child_models = [
        FileProject,
        GithubProject
    ]
    list_filter = [
        PolymorphicChildModelFilter
    ]


class FileProjectFileInline(admin.TabularInline):
    model = FileProjectFile


@admin.register(FileProject)
class FileProjectAdmin(PolymorphicChildModelAdmin):
    base_model = FileProject
    inlines = [
        FileProjectFileInline
    ]


@admin.register(GithubProject)
class GithubProjectAdmin(PolymorphicChildModelAdmin):
    base_model = GithubProject

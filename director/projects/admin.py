from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter
)

from .models import (
    Project,
    FilesProject, FilesProjectFile,
)


@admin.register(Project)
class ProjectAdmin(PolymorphicParentModelAdmin):
    base_model = Project
    child_models = [
        FilesProject,
    ]

    list_display = [
        '__str__', 'public', 'archive'
    ]
    list_filter = [
        PolymorphicChildModelFilter
    ]

    def archive(self, project):
        url = reverse('project_archive', args=[project.id])
        return format_html('<a href="{}">Archive</a>'.format(url))
    archive.short_description = 'Archive'


class FilesProjectFileInline(admin.TabularInline):
    model = FilesProjectFile


@admin.register(FilesProject)
class FilesProjectAdmin(PolymorphicChildModelAdmin):
    base_model = FilesProject
    inlines = [
        FilesProjectFileInline
    ]

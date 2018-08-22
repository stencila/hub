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
    FilesSource, FilesSourceFile,
    Source, SessionParameters)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 'public', 'archive'
    ]
    list_filter = [
        'public'
    ]

    def archive(self, project):
        url = reverse('project_archive', args=[project.id])
        return format_html('<a href="{}">Archive</a>'.format(url))

    archive.short_description = 'Archive'


@admin.register(Source)
class SourceAdmin(PolymorphicParentModelAdmin):
    base_model = Source
    child_models = [
        FilesSource,
    ]


class FilesSourceFileInline(admin.TabularInline):
    model = FilesSourceFile


@admin.register(FilesSource)
class FilesProjectAdmin(PolymorphicChildModelAdmin):
    base_model = FilesSource
    inlines = [
        FilesSourceFileInline
    ]


@admin.register(SessionParameters)
class SessionParametersAdmin(admin.ModelAdmin):
    pass

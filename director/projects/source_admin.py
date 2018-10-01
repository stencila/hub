from django.contrib import admin

from .models import Source, FileSource


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    pass


@admin.register(FileSource)
class FileSourceAdmin(admin.ModelAdmin):
    pass

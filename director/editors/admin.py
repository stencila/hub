from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Editor, NativeEditor


@admin.register(Editor)
class EditorAdmin(ModelAdmin):
    pass


@admin.register(NativeEditor)
class NativeEditorAdmin(ModelAdmin):
    pass

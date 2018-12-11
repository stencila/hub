from django import template
from django.urls import reverse

from projects.project_models import Project
from projects.source_item_models import DirectoryListEntry, DirectoryEntryType

register = template.Library()


@register.simple_tag
def source_path(project: Project, directory_entry: DirectoryListEntry):
    if directory_entry.is_directory and directory_entry.path:
        view_name = 'project_files_path'
        view_args = project.pk, directory_entry.path
        return reverse(view_name, args=view_args)

    if directory_entry.type == DirectoryEntryType.FILE:
        return reverse('file_source_open', args=(project.pk, directory_entry.source.pk, directory_entry.path))

    return ""

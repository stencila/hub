import typing

from django import template
from django.urls import reverse

from projects.project_models import Project
from projects.source_item_models import DirectoryListEntry, DirectoryEntryType
from projects.source_models import DiskFileSource

register = template.Library()


@register.simple_tag
def source_path(project: Project, directory_entry: DirectoryListEntry):
    if directory_entry.is_directory and directory_entry.path:
        view_name = 'project_files_path'
        view_args = project.pk, directory_entry.path
        return reverse(view_name, args=view_args)

    if directory_entry.type == DirectoryEntryType.FILE:
        if isinstance(directory_entry.source, DiskFileSource):
            return reverse('real_file_source_open', args=(project.pk, directory_entry.path))
        else:
            return reverse('file_source_open', args=(project.pk, directory_entry.source.pk, directory_entry.path))

    return ""


def mimetype_text_editable(mimetype: str) -> bool:
    if mimetype in ('Unknown', 'application/javascript', 'application/json', 'application/xml'):
        return True

    return '/' in mimetype and mimetype.split('/')[0] == 'text'


@register.filter
def is_text_editable(directory_entry: typing.Any) -> bool:
    if not isinstance(directory_entry, DirectoryListEntry):
        return False

    directory_entry = typing.cast(DirectoryListEntry, directory_entry)

    if directory_entry.is_directory or not directory_entry.mimetype:
        return False

    return mimetype_text_editable(directory_entry.mimetype)

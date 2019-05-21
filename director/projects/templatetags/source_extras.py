import typing
from os.path import splitext

from django import template
from django.urls import reverse

from lib.google_docs_facade import build_google_document_url
from projects.project_models import Project
from projects.source_item_models import DirectoryListEntry, DirectoryEntryType
from projects.source_models import DiskSource, GoogleDocsSource

register = template.Library()


@register.simple_tag
def source_path(project: Project, directory_entry: DirectoryListEntry) -> str:
    if isinstance(directory_entry.source, GoogleDocsSource):
        source = typing.cast(GoogleDocsSource, directory_entry.source)
        return build_google_document_url(source.doc_id)

    if directory_entry.is_directory and directory_entry.path:
        view_name = 'project_files_path'
        view_args = project.pk, directory_entry.path
        return reverse(view_name, args=view_args)

    if directory_entry.type == DirectoryEntryType.FILE:
        if isinstance(directory_entry.source, DiskSource):
            return reverse('disk_file_source_open', args=(project.pk, directory_entry.path))
        else:
            return reverse('file_source_open', args=(project.pk, directory_entry.source.pk, directory_entry.path))

    return ""


@register.simple_tag
def download_url(project: Project, directory_entry: DirectoryListEntry) -> str:
    if directory_entry.is_directory:
        return ''

    if isinstance(directory_entry.source, DiskSource):
        return reverse('disk_file_source_download', args=(project.pk, directory_entry.path))
    else:
        return reverse('file_source_download', args=(project.pk, directory_entry.source.pk, directory_entry.path))


def mimetype_text_editable(mimetype: str) -> bool:
    if mimetype in ('Unknown', 'application/javascript', 'application/json', 'application/xml'):
        return True

    return '/' in mimetype and mimetype.split('/')[0] == 'text'


@register.filter
def is_text_editable(directory_entry: typing.Any) -> bool:
    if not isinstance(directory_entry, DirectoryListEntry):
        return False

    directory_entry = typing.cast(DirectoryListEntry, directory_entry)

    if isinstance(directory_entry.source, GoogleDocsSource):
        return True

    if directory_entry.is_directory or not directory_entry.mimetype:
        return False

    return mimetype_text_editable(directory_entry.mimetype)


@register.filter
def is_main_file(directory_entry: typing.Any, project: typing.Any) -> bool:
    if not isinstance(directory_entry, DirectoryListEntry):
        return False

    directory_entry = typing.cast(DirectoryListEntry, directory_entry)

    if not isinstance(project, Project):
        return False

    project = typing.cast(Project, project)

    return directory_entry.path == project.main_file_path


@register.filter
def can_be_main_file(directory_entry: typing.Any, project: typing.Any) -> bool:
    if not isinstance(directory_entry, DirectoryListEntry):
        return False

    directory_entry = typing.cast(DirectoryListEntry, directory_entry)

    if not isinstance(project, Project):
        return False

    project = typing.cast(Project, project)

    if directory_entry.is_directory:
        return False

    return not is_main_file(directory_entry, project)


@register.filter
def edit_menu_text(directory_entry: typing.Any) -> str:
    if not isinstance(directory_entry, DirectoryListEntry):
        return ''

    directory_entry = typing.cast(DirectoryListEntry, directory_entry)

    if isinstance(directory_entry.source, GoogleDocsSource):
        return 'Open in Google Docs'

    return 'Open in Code Editor'


@register.filter
def file_icon(directory_entry: typing.Any) -> str:
    if not isinstance(directory_entry, DirectoryListEntry):
        return ''

    directory_entry = typing.cast(DirectoryListEntry, directory_entry)

    if directory_entry.is_directory:
        return 'folder'

    name, ext = splitext(directory_entry.name)

    if ext:
        ext = ext[1:].lower()

    if ext in ['py', 'r', 'rmd', 'json', 'js', 'xml', 'html']:
        return 'file-code'

    return 'file'

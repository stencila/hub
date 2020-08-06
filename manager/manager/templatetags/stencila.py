"""
Custom template tags.

All in one file so that it is easy just to `{% load stencila %}`
in templates.
"""

from uuid import uuid4

from django import template
from django.conf import settings
from django.db.models import fields
from django.shortcuts import reverse
from django.urls import resolve
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

from projects.models.files import FileFormat, FileFormats

register = template.Library()


@register.simple_tag(takes_context=True)
def primary_domain_url(context, *args):
    """
    Get a URL at the primary domain.
    """
    protocol = "https" if context["request"].is_secure() else "http"
    return protocol + "://" + settings.PRIMARY_DOMAIN + reverse(args[0], args=args[1:])


@register.simple_tag(takes_context=True)
def is_active(context, name):
    """
    Return "is-active" if the current path resolves to a view starting with `name`.

    Used to add the "is-active" CSS class to elements.
    Most useful when view names reflect the view hierarchy.
    e.g. `ui-accounts-teams-list` and `ui-accounts-teams-update`
    with both be "is-active" in this case:

        class="{% is_active 'ui-accounts-teams' %}"
    """
    match = resolve(context["request"].path)
    return "is-active" if match.url_name.startswith(name) else ""


@register.filter
def field_element(field, default=None):
    """
    Get the HTML tag name for a serializer field.

    See the `field_class_lookup` below.
    """
    vars = field_class_lookup[field]
    return vars.get("field_element", "input")


@register.filter
def input_type(field):
    """
    Get the <input> element "type" attribute for a serializer field.

    See the `field_class_lookup` below.
    """
    vars = field_class_lookup[field]
    return vars.get("input_type", "")


@register.simple_tag
def uuid():
    """
    Get a UUID.

    Used for generating unique element ids in templates.
    """
    return uuid4()


@register.filter
def format_bytes(num, suffix="B"):
    """
    Format bytes as a human readable string.

    Thanks to https://stackoverflow.com/a/1094933.
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


@register.filter
def remove_prefix(text, prefix):
    """
    Remove a prefix from a string.

    If the string does not start with the prefix then
    nothing is removed.
    """
    if prefix:
        return text[text.startswith(prefix) and len(prefix) :]
    else:
        return text


@register.simple_tag
def file_format_convert_to_options(format_id=None, mimetype=None):
    """
    Get the list of file formats that a can be converted to.
    """
    try:
        return FileFormats.from_id_or_mimetype(format_id, mimetype).convert_to_options
    except ValueError:
        return FileFormat.default_convert_to_options()


@register.simple_tag
def file_format_icon(format_id=None, mimetype=None):
    """
    Get the icon class for a file format.
    """
    try:
        return FileFormats.from_id_or_mimetype(format_id, mimetype).icon_class
    except ValueError:
        return FileFormat.default_icon_class()


# fmt: off

field_class_lookup = ClassLookupDict({
    serializers.Field: {
        'field_element': 'input',
        'input_type': 'text'
    },
    serializers.EmailField: {
        'field_element': 'input',
        'input_type': 'email'
    },
    serializers.URLField: {
        'field_element': 'input',
        'input_type': 'url'
    },
    serializers.IntegerField: {
        'field_element': 'input',
        'input_type': 'number'
    },
    serializers.FloatField: {
        'field_element': 'input',
        'input_type': 'number'
    },
    serializers.DateTimeField: {
        'field_element': 'input',
        'input_type': 'datetime-local'
    },
    serializers.DateField: {
        'field_element': 'input',
        'input_type': 'date'
    },
    serializers.TimeField: {
        'field_element': 'input',
        'input_type': 'time'
    },
    serializers.FileField: {
        'field_element': 'input',
        'input_type': 'file'
    },
    serializers.BooleanField: {
        'field_element': 'checkbox'
    },
    serializers.ChoiceField: {
        'field_element': 'select'
    },
    serializers.MultipleChoiceField: {
        'field_element': 'select_multiple'
    },
    serializers.RelatedField: {
        'field_element': 'select',
    },
    serializers.ManyRelatedField: {
        'field_element': 'select_multiple'
    },
    serializers.Serializer: {
        'field_element': 'fieldset'
    },
    serializers.ListSerializer: {
        'field_element': 'list_fieldset'
    },
    serializers.ListField: {
        'field_element': 'list_field'
    },
    serializers.DictField: {
        'field_element': 'dict_field'
    },
    serializers.FilePathField: {
        'field_element': 'select'
    },
    fields.TextField: {
        'field_element': 'textarea'
    },
    serializers.JSONField: {
        'field_element': 'textarea'
    },
})

# fmt: on

"""
Custom template tags.

All in one file so that it is easy just to `{% load stencila %}`
in templates.
"""

from uuid import uuid4

from django import template
from django.db.models import fields
from django.urls import resolve
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

register = template.Library()


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
def formatbytes(num, suffix="B"):
    """
    Format bytes as a human readable string.

    Thanks to https://stackoverflow.com/a/1094933.
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


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

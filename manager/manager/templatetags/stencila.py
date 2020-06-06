"""
Custom template tags.

All in one file so that it is easy just to `{% load stencila %}`
in templates.
"""

from django import template
from django.shortcuts import reverse
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

register = template.Library()


@register.simple_tag(takes_context=True)
def is_active(context, name, *args):
    """
    Return "is-active" if the current path matches that for a named view.

    Used to add the "is-active" CSS class to elements e.g.

        class="{% is_active 'ui-account-profile' account.name %}"
    """
    return "is-active" if context["request"].path == reverse(name, args=args) else ""


@register.filter
def field_element(field):
    """
    Get the HTML tag name for a serializer field.

    See the `field_class_lookup` below.
    """
    vars = dict(field_class_lookup[field])
    return vars.get("field_element", "input")


@register.filter
def input_type(field):
    """
    Get the <input> element "type" attribute for a serializer field.

    See the `field_class_lookup` below.
    """
    vars = dict(field_class_lookup[field])
    return vars.get("input_type", "")


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
        'field_element': 'select',
    },
    serializers.MultipleChoiceField: {
        'field_element': 'select_multiple',
    },
    serializers.RelatedField: {
        'field_element': 'select',
    },
    serializers.ManyRelatedField: {
        'field_element': 'select_multiple',
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
        'field_element': 'select',
    },
    serializers.JSONField: {
        'field_element': 'textarea',
    },
})

# fmt: on

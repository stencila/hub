from django import template
from django.utils.safestring import mark_safe
from rest_framework.renderers import HTMLFormRenderer

register = template.Library()


@register.simple_tag
def render_form(serializer):
    """
    Render an API serializer as a form.

    This is an alternative implementation of `rest_framework`'s
    `render_form` that does not have the `template_pack` parameter.
    """
    renderer = HTMLFormRenderer()
    return renderer.render(serializer.data, None, {"style": {}})


@register.simple_tag
def render_field(field):
    """
    Render a API serializer field as a form element.

    This is an alternative implmenetation of `rest_framework`'s
    `render_field` that does not require the `style` parameter.
    """
    renderer = HTMLFormRenderer()
    return renderer.render_field(field, {})


@register.simple_tag
def handle_form(is_update=False, success_url=None):
    """
    Create a <script> to handle form submission.

    See the `handleForm` function in `form-helpers.js` for
    what this function does and it's parameters.
    """
    return mark_safe(
        "<script>handleForm({is_update}, {success_url})</script>".format(
            is_update="true" if is_update else "false",
            success_url="'{}'".format(success_url) if success_url else "null",
        )
    )

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
from django.urls.exceptions import Resolver404
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

from projects.models.files import FileFormat, FileFormats
from users.models import get_name as user_get_name

register = template.Library()


@register.simple_tag(takes_context=True)
def primary_domain_url(context, *args):
    """
    Get a URL at the primary domain.
    """
    protocol = "https" if context["request"].is_secure() else "http"
    return protocol + "://" + settings.PRIMARY_DOMAIN + reverse(args[0], args=args[1:])


@register.simple_tag(takes_context=True)
def query_params(context, exclude=["page"]):
    """
    Get the query parameters from the current request to include in a new URL.
    """
    params = context["request"].GET.copy()

    if "page" in params:
        del params["page"]

    return params.urlencode()


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
    try:
        match = resolve(context["request"].path)
    except Resolver404:
        return ""
    return (
        "is-active"
        if match and match.url_name and match.url_name.startswith(name)
        else ""
    )


@register.simple_tag(takes_context=True)
def is_an_account_settings_page(context, account):
    """
    Return `true` if the current path is for one of the account "settings" pages.

    Used to determine whether or not to show the settings submenu.
    """
    path = context["request"].path
    return (
        path.startswith("/me/")
        or path.startswith(f"/{account.name}/profile")
        or path.startswith(f"/{account.name}/publishing")
    )


@register.simple_tag(takes_context=True)
def is_users_personal_account(context, account):
    """
    Return `true` if the current path is for the user's personal account.

    Used to determine which items to show in the settings submenu.
    """
    request = context["request"]
    return account.is_personal and (
        request.path.startswith("/me/")
        or request.user.is_authenticated
        and request.path.startswith(f"/{request.user.username}/")
    )


@register.simple_tag(takes_context=True)
def is_selected(context, name, value):
    """
    Return "selected" if current request URL has a matching value for the query parameter.

    Used to add the "selected" attribute to a `<select><option>` based on the URL e.g.

        <option value="member" {% is_selected "role" "member" %}>{% trans "I am a member" %}</option>
    """
    return "selected" if context["request"].GET.get(name) == value else ""


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
def project_content_url(project, **kwargs):
    """
    Get the URL for a file path within a project.

    This can significantly reduce the number of queries instead
    of fetching the project and account for every file in a list
    which happens when using `{{ file.download_url }}`.
    """
    return project.content_url(**kwargs)


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


@register.filter
def split_text(text, length=280):
    """
    Given a string, split it into two at the given length.
    """
    return [text[:length], text[length:]]


@register.filter
def tier_count(count):
    """
    If a tier quota is 9999, treat it as unlimited.
    """
    if count == 9999:
        return "Unlimited"
    else:
        return count


@register.filter
def get_name(user):
    """
    Get the best name to display for a user.
    """
    return user_get_name(user)


@register.tag
def render_node(parser, token):
    """
    Parse a render_node template tag.
    """
    try:
        tag_name, node = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument, the node to be rendered"
            % token.contents.split()[0]
        )
    return RenderNode(node)


class RenderNode(template.Node):
    """
    Render a Stencila Schema node.

    This is primarily intended for rendering the content of a
    `CreativeWork` node (e.g. a `Article`, `Review` or `Comment`)
    without having to delegate to Encoda. See the templates in
    `manager/manager/templates/nodes/`.
    """

    def __init__(self, node):
        self.node = template.Variable(node)

    def render(self, context: template.Context):
        """
        Render the node.
        """
        try:
            node = self.node.resolve(context)
            if isinstance(node, dict):
                node_type = node.get("type")
                if node_type:
                    try:
                        # Try to render a template for the type
                        return self.render_template(
                            context, f"nodes/{node_type}.html", node
                        )
                    except template.TemplateDoesNotExist as exc:
                        # In debug mode raise an exception so we know to add
                        # a template
                        if context.template.engine.debug:
                            raise exc
                        # In production, see if the node has content and if so
                        # render that
                        if "content" in node:
                            return self.render_template(
                                context, "nodes/content.html", node
                            )
                        # Otherwise just return a string.
                        return ""
            return f"{node}"
        except template.VariableDoesNotExist:
            return ""

    def render_template(self, context: template.Context, template_name: str, node):
        """
        Render a template with the node in the context.
        """
        templ = context.template.engine.get_template(template_name)
        return templ.render(
            template.Context({"node": node}, autoescape=context.autoescape)
        )


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

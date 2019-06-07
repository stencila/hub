from django.templatetags.static import StaticNode

import _version


def monkey_patch():
    old_static_node_render = StaticNode.render

    def new_static_node_render(cls, context):
        static_path = old_static_node_render(cls, context)

        if static_path:
            joiner = '&' if '?' in static_path else '?'
            return '{}{}v={}'.format(static_path, joiner, _version.__version__)

        return static_path

    StaticNode.render = new_static_node_render

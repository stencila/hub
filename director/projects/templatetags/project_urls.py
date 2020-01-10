import typing

from django import template

from projects.project_models import Project
from projects.url_helpers import project_url_reverse

register = template.Library()


class ProjectUrlNode(template.Node):
    project: template.Variable
    view_name: template.Variable
    args: typing.List[template.Variable]

    def __init__(self, view_name: str, project: str, args: str) -> None:
        self.project = template.Variable(project)
        self.view_name = template.Variable(view_name)
        self.args = list(map(template.Variable, args))

    def render(self, context):
        project: Project = self.project.resolve(context)
        if not isinstance(project, Project):
            raise TypeError('The first variable to the templatetag must be a Project instance.')

        view_name: str = self.view_name.resolve(context)

        if not isinstance(view_name, str):
            raise TypeError('The view name is expected to be a str')

        resolved_args = list(map(lambda a: a.resolve(context), self.args))

        return project_url_reverse(view_name, resolved_args, project=project)


@register.tag
def project_url(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, view_name, project, *args = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires at least two args" % token.contents.split()[0]
        )

    return ProjectUrlNode(view_name, project, args)

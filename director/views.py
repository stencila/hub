from django.views.generic import (
    TemplateView
)

from projects.models import Project
from editors.models import Editor
#from hosts.models import Host


class HomeView(TemplateView):
    template_name = 'home.html'


class OpenView(TemplateView):
    """
    Open a project with an editor
    """
    template_name = 'open.html'

    def get(self, request):
        # If no project specified then we'll
        # ask for it in the template
        url = request.GET.get('project')
        if not url:
            return self.render_to_response()

        # Get, or create a project
        project, _ = Project.get_or_create_from_url(
            url=url,
            creator=request.user
        )

        # Create an editor for the project
        # The `editor` parameter is optional
        editor = Editor.create(
            type=request.GET.get('editor'),
            project=project,
            creator=request.user
        )

        # Create an execution host for the project
        # The `host` parameter is optional
        #host = Host.create(
        #    type=request.GET.get('host'),
        #    project=project,
        #    creator=request.user
        #)
        host = None

        # Render the progress template
        return self.render_to_response(dict(
            project=project,
            editor=editor,
            host=host
        ))

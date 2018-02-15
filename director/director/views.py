from django.http import Http404
from django.views.generic import TemplateView
from .auth import login_guest_user
from .storer import storers
from .models import Project

class FrontPageView(TemplateView):
    template_name = 'index.html'

class SignInView(TemplateView):
    template_name = 'signin.html'

class ProjectView(TemplateView):
    template_name = 'project.html'

    def dispatch(self, request, *args, **kwargs):
        self.storer_name = kwargs.get('storer')
        self.path = kwargs.get('path')
        return super(ProjectView, self).dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        try:
            storer = storers[self.storer_name](self.path)
        except:
            raise Http404

        if storer.is_accessible():
            if not request.user.is_authenticated:
                login_guest_user(request)

            address = storer.get_address()
            _, p = Project.objects.get_or_create(creator=request.user, address=address)

        return super(ProjectView, self).get(request, **kwargs)

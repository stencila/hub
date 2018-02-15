from django.views.generic import TemplateView

class FrontPageView(TemplateView):
    template_name = 'index.html'

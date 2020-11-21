from django.urls import path, re_path
from django.shortcuts import redirect, get_object_or_404

from dois.models import Doi


def doi_redirect(request, doi):
    """
    View to redirect from a DOI to its node.
    """
    doi_object = get_object_or_404(Doi, doi=doi)
    url = doi_object.node.get_absolute_url()
    return redirect(url)


urlpatterns = [
    re_path(r"(?P<doi>.*)", doi_redirect, name="ui-dois-redirect",),
]

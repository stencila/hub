from django.test import RequestFactory

from manager.api.views.docs import schema_view


def run(*args):
    response = schema_view(RequestFactory().get("/api/schema"))
    response.render()
    print(response.content.decode("utf-8"))

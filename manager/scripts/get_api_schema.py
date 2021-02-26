from django.test import RequestFactory

from manager.api.views.docs import schema_view


def run(to):
    response = schema_view(RequestFactory().get("/api/schema"))
    response.render()
    with open(to, "wb") as file:
        file.write(response.content)

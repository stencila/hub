import os.path

from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    """A custom schema generator."""

    def get_schema(self, *args, **kwargs):
        """Override to alter the base path of the schema."""
        schema = super().get_schema(*args, **kwargs)
        schema.basePath = "/api"
        return schema


with open(
    os.path.join(os.path.dirname(__file__), "docs.md"), "r", encoding="utf-8"
) as file:
    description = file.read()

schema_view = get_schema_view(
    openapi.Info(
        title="Stencila Hub API", default_version="v1", description=description,
    ),
    urlconf="urls_api",
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomOpenAPISchemaGenerator,
).without_ui()

swagger_view = TemplateView.as_view(template_name="api_swagger.html")

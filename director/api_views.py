from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        schema.basePath = "/api"
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="Stencila Hub API",
        default_version="v1",
        description="RESTful API for the Stencila Hub",
    ),
    urlconf="api_urls",
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomOpenAPISchemaGenerator,
).without_ui()

from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from auth.api_urls import urlpatterns as auth_urls
from projects.api_urls import urlpatterns as project_urls
from users.api_urls import urlpatterns as user_urls

urlpatterns = [
    # Provide /login and /logout URLs for DRF's browsable API interface
    path('', include('rest_framework.urls')),
    
    # API schema
    path('schema/', get_schema_view(
        title="Stencila Hub API",
        url="/api/",
        urlconf='api_urls',
        description="RESTful API for the Stencila Hub"
    ), name='api_schema'),
    
    # ReDoc API documentation
    # ReDoc is nice (although it does not have the ability to try executing API endpoints (?))
    # but it does not play nicely with the `operationId`s produced by DRF (it leads to very busy
    # sidebar). Also, styles clash with Hub styles. Will leave this as placeholder but not enable it.
    #  path('docs/', TemplateView.as_view(
    #     template_name='api_redoc.html'
    #  ), name='api_docs'),
    
    # Swagger UI
    path('ui/', TemplateView.as_view(
        template_name='api_swagger.html',
    ), name='api_ui'),
    
    # API URLs for each app
    path('auth/', include(auth_urls)),
    path('projects/', include(project_urls)),
    path('users/', include(user_urls)),
]

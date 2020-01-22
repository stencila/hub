from django.conf import settings
from django.urls import include, path, re_path

from projects.project_host_views import (ProjectHostManifestView, ProjectHostSessionsView, ProjectSessionRequestView,
                                         ProjectSessionSetupView)
from projects.project_views import (ProjectListView, ProjectCreateView, ProjectSettingsSessionsView,
                                    ProjectNamedRedirect)

urlpatterns = [
    # Generic views
    path('', ProjectListView.as_view(), name='project_list'),

    path('create/', ProjectCreateView.as_view(), name='project_create'),

    path('<int:pk>/', ProjectNamedRedirect.as_view(), name='project_named_redirect'),
    path('<int:pk>/<path:path>', ProjectNamedRedirect.as_view(), name='project_named_redirect_path'),
    # Per project Host API
    # TODO: These are probably redundant – replace with slug?
    path('<str:token>/host/', include([
        path('v0/', include([
            path('manifest', ProjectHostManifestView.as_view(), {'version': 0}),
            re_path(r'^environ/(?P<environ>.*)', ProjectHostSessionsView.as_view(api_version=0),
                    name='session_start_v0'),
            path('session-queue', ProjectSessionRequestView.as_view(api_version=0), name='session_queue_v0')
        ])),
        path('v1/', include([
            path('manifest', ProjectHostManifestView.as_view(), {'version': 1}),
            re_path(r'^sessions/(?P<environ>.*)', ProjectHostSessionsView.as_view(api_version=1),
                    name='session_start_v1'),
            path('session-queue', ProjectSessionRequestView.as_view(api_version=1), name='session_queue_v1')
        ]))
    ])),

    path('<str:token>/session-setup/<path:environ>', ProjectSessionSetupView.as_view(),
         name='project_session_setup'),

    # Type-specific views
    # path('files/<int:pk>/', FilesSourceReadView.as_view(), name='filesproject_read'),
    # path('files/<int:pk>/update/', FilesSourceUpdateView.as_view(), name='filesproject_update'),
    # path('files/<int:pk>/upload/', FilesSourceUploadView.as_view(), name='filesproject_upload'),
    # path('files/<int:pk>/remove/<int:file>/', FilesProjectRemoveView.as_view(), name='filesproject_remove'),
]

if settings.FEATURES['PROJECT_SESSION_SETTINGS']:
    urlpatterns.append(
        path('<int:pk>/settings/sessions', ProjectSettingsSessionsView.as_view(), name='project_settings_sessions')
    )

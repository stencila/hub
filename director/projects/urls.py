from django.urls import include, path, re_path

from .views import (
    ProjectListView,

    ProjectCreateView,

    ProjectGeneralView,
    ProjectFilesView,
    ProjectActivityView,
    ProjectSharingView,

    ProjectSettingsMetadataView,
    ProjectSettingsAccessView,
    ProjectSettingsSessionsView,

    ProjectHostManifestView,
    ProjectHostSessionsView,
    ProjectArchiveView,

    ProjectDeleteView,
)

urlpatterns = [
    # Generic views
    path('', ProjectListView.as_view(), name='project_list'),

    path('create/', ProjectCreateView.as_view(), name='project_create'),

    path('<int:pk>/general/', ProjectGeneralView.as_view(), name='project_update'),
    path('<int:pk>/files/', ProjectFilesView.as_view(), name='project_files'),
    path('<int:pk>/activity/', ProjectActivityView.as_view(), name='project_activity'),
    path('<int:pk>/sharing/', ProjectSharingView.as_view(), name='project_sharing'),
    path('<int:pk>/settings/metadata', ProjectSettingsMetadataView.as_view(), name='project_settings_metadata'),
    path('<int:pk>/settings/access', ProjectSettingsAccessView.as_view(), name='project_settings_access'),
    path('<int:pk>/settings/sessions', ProjectSettingsSessionsView.as_view(), name='project_settings_sessions'),


    #path('update/save-general', ProjectGeneralSaveView.as_view(), name='project_general_save'),
    #path('update/save-session-parameters', ProjectSessionParametersSaveView.as_view(),
    #     name='project_session_parameters_save'),
    #path('update/save-access', ProjectAccessSaveView.as_view(), name='project_access_save'),

    #path('<int:pk>/sessions/', ProjectSessionsListView.as_view(), name='project_sessions'),

    # Per project Host API
    path('<str:token>/host/', include([
        path('v0/', include([
            path('manifest', ProjectHostManifestView.as_view(), {'version': 0}),
            re_path(r'^environ/(?P<environ>.*)', ProjectHostSessionsView.as_view())
        ])),
        path('v1/', include([
            path('manifest', ProjectHostManifestView.as_view(), {'version': 1}),
            re_path(r'^sessions/(?P<environ>.*)', ProjectHostSessionsView.as_view())
        ]))
    ])),

    path('<int:pk>/archive/', ProjectArchiveView.as_view(), name='project_archive'),


    path('<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),

    # Type-specific views
    #path('files/<int:pk>/', FilesSourceReadView.as_view(), name='filesproject_read'),
    #path('files/<int:pk>/update/', FilesSourceUpdateView.as_view(), name='filesproject_update'),
    #path('files/<int:pk>/upload/', FilesSourceUploadView.as_view(), name='filesproject_upload'),
    #path('files/<int:pk>/remove/<int:file>/', FilesProjectRemoveView.as_view(), name='filesproject_remove'),
]

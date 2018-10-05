from django.urls import include, path, re_path

from projects.project_host_views import (ProjectHostManifestView, ProjectHostSessionsView, ProjectSessionRequestView)
from projects.project_views import (ProjectListView, ProjectCreateView, ProjectOverviewView, ProjectFilesView,
                                    ProjectActivityView, ProjectSharingView, ProjectRoleUpdateView,
                                    ProjectSettingsMetadataView, ProjectSettingsAccessView, ProjectSettingsSessionsView,
                                    ProjectArchiveView, ProjectDeleteView)
from projects.source_views import (FileSourceCreateView, FileSourceUploadView, DropboxSourceCreateView,
                                   GithubSourceCreateView, SourceOpenView, SourceUpdateView, SourceDeleteView)

urlpatterns = [
    # Generic views
    path('', ProjectListView.as_view(), name='project_list'),

    path('create/', ProjectCreateView.as_view(), name='project_create'),

    path('<int:pk>/', ProjectOverviewView.as_view(), name='project_overview'),

    path('<int:pk>/files/browse/', ProjectFilesView.as_view(), name='project_files'),
    path('<int:pk>/files/browse/<path:path>', ProjectFilesView.as_view(), name='project_files_path'),
    path('<int:pk>/files/create', FileSourceCreateView.as_view(), name='filesource_create'),
    path('<int:pk>/files/upload', FileSourceUploadView.as_view(), name='filesource_upload'),

    path('<int:pk>/files/link/dropbox', DropboxSourceCreateView.as_view(), name='dropboxsource_create'),
    path('<int:pk>/files/link/github', GithubSourceCreateView.as_view(), name='githubsource_create'),

    path('<int:project_pk>/files/<int:pk>/open', SourceOpenView.as_view(), name='source_open'),
    path('<int:project_pk>/files/<int:pk>/update', SourceUpdateView.as_view(), name='source_update'),
    path('<int:project_pk>/files/<int:pk>/delete', SourceDeleteView.as_view(), name='source_delete'),

    path('<int:pk>/activity/', ProjectActivityView.as_view(), name='project_activity'),
    path('<int:pk>/sharing/', ProjectSharingView.as_view(), name='project_sharing'),
    path('<int:pk>/sharing/roles', ProjectRoleUpdateView.as_view(), name='project_sharing_roles'),
    path('<int:pk>/settings/metadata', ProjectSettingsMetadataView.as_view(), name='project_settings_metadata'),
    path('<int:pk>/settings/access', ProjectSettingsAccessView.as_view(), name='project_settings_access'),
    path('<int:pk>/settings/sessions', ProjectSettingsSessionsView.as_view(), name='project_settings_sessions'),

    # Per project Host API
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

    path('<int:pk>/archive/', ProjectArchiveView.as_view(), name='project_archive'),

    path('<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),

    # Type-specific views
    # path('files/<int:pk>/', FilesSourceReadView.as_view(), name='filesproject_read'),
    # path('files/<int:pk>/update/', FilesSourceUpdateView.as_view(), name='filesproject_update'),
    # path('files/<int:pk>/upload/', FilesSourceUploadView.as_view(), name='filesproject_upload'),
    # path('files/<int:pk>/remove/<int:file>/', FilesProjectRemoveView.as_view(), name='filesproject_remove'),
]

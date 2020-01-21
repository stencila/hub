from django.conf import settings
from django.urls import include, path, re_path

from lib.constants import ProjectUrlRoot
from projects.project_host_views import (ProjectHostManifestView, ProjectHostSessionsView, ProjectSessionRequestView,
                                         ProjectSessionSetupView)
from projects.project_views import (ProjectListView, ProjectCreateView, ProjectOverviewView, ProjectFilesView,
                                    ProjectActivityView, ProjectSharingView, ProjectRoleUpdateView,
                                    ProjectSettingsMetadataView, ProjectSettingsAccessView, ProjectSettingsSessionsView,
                                    ProjectArchiveDownloadView, ProjectDeleteView, ProjectPullView, ProjectArchiveView,
                                    ProjectNamedArchiveDownloadView, ProjectExecutaView,
                                    PublishedContentView, PublishedMediaView, PublishedListView)
from projects.source_views import (FileSourceUploadView, DropboxSourceCreateView,
                                   GithubSourceCreateView, SourceOpenView,
                                   DiskFileSourceOpenView, GoogleDocsSourceCreateView,
                                   SourceConvertView, SourceDownloadView, DiskFileSourceDownloadView)

urlpatterns = [
    # Generic views
    path('', ProjectListView.as_view(), name='project_list'),

    path('create/', ProjectCreateView.as_view(), name='project_create'),

    path('<int:pk>/', include([
        path('', ProjectOverviewView.as_view(), name='project_overview'),

        path(ProjectUrlRoot.files.value + '/', include([
            path('browse/', ProjectFilesView.as_view(), name='project_files'),
            path('browse/<path:path>', ProjectFilesView.as_view(), name='project_files_path'),
            path('upload/', FileSourceUploadView.as_view(), name='filesource_upload'),
            path('pull/', ProjectPullView.as_view(), name='project_pull'),
            path('link/dropbox/', DropboxSourceCreateView.as_view(), name='dropboxsource_create'),
            path('link/github/', GithubSourceCreateView.as_view(), name='githubsource_create'),
            path('link/googledocs/', GoogleDocsSourceCreateView.as_view(), name='googledocssource_create'),
            path('convert/', SourceConvertView.as_view(), name='source_convert')
        ])),

        path(ProjectUrlRoot.activity.value + '/', ProjectActivityView.as_view(), name='project_activity'),
        path(ProjectUrlRoot.sharing.value + '/', ProjectSharingView.as_view(), name='project_sharing'),
        path(ProjectUrlRoot.sharing.value + '/roles/', ProjectRoleUpdateView.as_view(), name='project_sharing_roles'),
        path(ProjectUrlRoot.settings.value + '/metadata/', ProjectSettingsMetadataView.as_view(),
             name='project_settings_metadata'),
        path(ProjectUrlRoot.settings.value + '/access/', ProjectSettingsAccessView.as_view(),
             name='project_settings_access'),
        path(ProjectUrlRoot.archives.value + '/', ProjectArchiveView.as_view(), name='project_archives'),
        path(ProjectUrlRoot.archives.value + '/<name>', ProjectNamedArchiveDownloadView.as_view(),
             name='project_named_archive_download'),

        path(ProjectUrlRoot.archive.value + '/', ProjectArchiveDownloadView.as_view(), name='project_archive'),
        path(ProjectUrlRoot.delete.value + '/', ProjectDeleteView.as_view(), name='project_delete'),
        path(ProjectUrlRoot.executa.value + '/', ProjectExecutaView.as_view(), name='project_executa'),

        path(ProjectUrlRoot.published.value + '/', PublishedListView.as_view(),
             name='project_published_list'),
        re_path(r'^(?P<path>.*)/\d+\.html\.media/(?P<media_path>.*)', PublishedMediaView.as_view(),
                name='project_published_media_view'),
        path('<path:path>/', PublishedContentView.as_view(),
             name='project_published_content'),
    ])),

    path('<int:project_pk>/' + ProjectUrlRoot.files.value + '/<int:pk>/open/<path:path>', SourceOpenView.as_view(),
         name='file_source_open'),
    path('<int:project_pk>/' + ProjectUrlRoot.files.value + '/open/<path:path>', DiskFileSourceOpenView.as_view(),
         name='disk_file_source_open'),

    path('<int:project_pk>/' + ProjectUrlRoot.files.value + '/<int:pk>/download/<path:path>',
         SourceDownloadView.as_view(), name='file_source_download'),
    path('<int:project_pk>/' + ProjectUrlRoot.files.value + '/download/<path:path>',
         DiskFileSourceDownloadView.as_view(), name='disk_file_source_download'),

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

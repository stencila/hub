from django.urls import path, include, re_path
from django.views.generic import RedirectView

import projects.views.publication_views
from lib.constants import ProjectUrlRoot
from projects.views import project_views, snapshot_views, source_views

urlpatterns = [
    # These patterns are listed in the same order they appear in the sidebar menu (more or less)
    path('', project_views.ProjectOverviewView.as_view(), name='project_overview'),

    path(ProjectUrlRoot.files.value + '/', include([
        path('', RedirectView.as_view(pattern_name='project_files', permanent=True)),
        path('browse/', project_views.ProjectFilesView.as_view(), name='project_files'),
        path('browse/<path:path>', project_views.ProjectFilesView.as_view(), name='project_files_path'),

        path('upload/', source_views.FileSourceUploadView.as_view(), name='filesource_upload'),
        path('pull/', project_views.ProjectPullView.as_view(), name='project_pull'),

        path('link/dropbox/', source_views.DropboxSourceCreateView.as_view(),
             name='dropboxsource_create'),
        path('link/github/', source_views.GithubSourceCreateView.as_view(), name='githubsource_create'),
        path('link/googledocs/', source_views.GoogleDocsSourceCreateView.as_view(),
             name='googledocssource_create'),
        path('convert/', source_views.SourceConvertView.as_view(), name='source_convert'),

        path('open/<path:path>', source_views.SourceOpenView.as_view(),
             name='file_source_open'),

        path('download/<path:path>', source_views.SourceDownloadView.as_view(),
             name='file_source_download'),

        re_path(r'^preview/(?P<pi_pk>\d+)\.html\.media/(?P<media_path>.*)',
                projects.views.publication_views.PreviewMediaView.as_view(),
                name='project_preview_media_view'),
        path('preview/<path:path>', projects.views.publication_views.SourcePreviewView.as_view(),
             name='file_source_preview'),
    ])),
    path(ProjectUrlRoot.archives.value + '/', project_views.ProjectArchiveView.as_view(), name='project_archives'),
    path(ProjectUrlRoot.archives.value + '/<name>', project_views.ProjectNamedArchiveDownloadView.as_view(),
         name='project_named_archive_download'),

    path(ProjectUrlRoot.activity.value + '/', project_views.ProjectActivityView.as_view(),
         name='project_activity'),

    path(ProjectUrlRoot.sharing.value + '/', project_views.ProjectSharingView.as_view(), name='project_sharing'),
    path(ProjectUrlRoot.sharing.value + '/roles/', project_views.ProjectRoleUpdateView.as_view(),
         name='project_sharing_roles'),
    path(ProjectUrlRoot.settings.value + '/metadata/', project_views.ProjectSettingsMetadataView.as_view(),
         name='project_settings_metadata'),
    path(ProjectUrlRoot.settings.value + '/access/', project_views.ProjectSettingsAccessView.as_view(),
         name='project_settings_access'),

    path(ProjectUrlRoot.snapshots.value + '/', include([
        path('', project_views.ProjectSnapshotListView.as_view(), name='project_snapshots'),
        path('<int:version>/browse/', snapshot_views.FileBrowserView.as_view(), name='snapshot_files'),
        path('<int:version>/browse/<path:path>', snapshot_views.FileBrowserView.as_view(),
             name='snapshot_files_path'
             ),
        path('<int:version>/download/<path:path>', snapshot_views.DownloadView.as_view(),
             name='snapshot_files_download'
             ),
        path('<int:version>/view/<path:path>', snapshot_views.ContentView.as_view(),
             name='snapshot_files_view'
             ),
        re_path(r'^(?P<version>\d+)/preview/(?P<pi_pk>\d+)\.html\.media/(?P<media_path>.*)',
                snapshot_views.PreviewMediaView.as_view(),
                name='project_preview_media_view'),
        path('<int:version>/preview/<path:path>', snapshot_views.PreviewView.as_view(),
             name='snapshot_files_preview'
             )
    ])),

    path(ProjectUrlRoot.delete.value + '/', project_views.ProjectDeleteView.as_view(), name='project_delete'),

    path(ProjectUrlRoot.executa.value + '/', project_views.ProjectExecutaView.as_view(), name='project_executa'),

    path(ProjectUrlRoot.published.value + '/', projects.views.publication_views.PublishedListView.as_view(),
         name='project_published_list'),
    re_path(r'^(?P<path>.*)/\d+\.html\.media/(?P<media_path>.*)',
            projects.views.publication_views.PublishedMediaView.as_view(),
            name='project_published_media_view'),
    path('<path:path>/', projects.views.publication_views.PublishedContentView.as_view(),
         name='project_published_content'),
]

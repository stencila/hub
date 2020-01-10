from django.urls import path

from projects import project_views
from projects import source_views

urlpatterns = [
    # These patterns are listed in the same order they appear in the sidebar menu (more or less)
    path('', project_views.ProjectOverviewView.as_view(), name='project_overview_slug'),

    path('files/browse/', project_views.ProjectFilesView.as_view(), name='project_files_slug'),
    path('files/browse/<path:path>', project_views.ProjectFilesView.as_view(), name='project_files_path_slug'),

    path('files/upload/', source_views.FileSourceUploadView.as_view(), name='filesource_upload_slug'),
    path('files/pull/', project_views.ProjectPullView.as_view(), name='project_pull_slug'),

    path('<int:pk>/files/link/dropbox/', source_views.DropboxSourceCreateView.as_view(),
         name='dropboxsource_create_slug'),
    path('files/link/github/', source_views.GithubSourceCreateView.as_view(), name='githubsource_create_slug'),
    path('<int:pk>/files/link/googledocs/', source_views.GoogleDocsSourceCreateView.as_view(),
         name='googledocssource_create_slug'),
    path('files/convert/', source_views.SourceConvertView.as_view(), name='source_convert_slug'),

    path('files/<int:pk>/open/<path:path>', source_views.SourceOpenView.as_view(),
         name='file_source_open_slug'),
    path('files/open/<path:path>', source_views.DiskFileSourceOpenView.as_view(),
         name='disk_file_source_open_slug'),

    path('files/<int:pk>/download/<path:path>', source_views.SourceDownloadView.as_view(),
         name='file_source_download_slug'),
    path('files/download/<path:path>', source_views.DiskFileSourceDownloadView.as_view(),
         name='disk_file_source_download_slug'),

    path('archives/', project_views.ProjectArchiveView.as_view(), name='project_archives_slug'),
    path('archives/<name>', project_views.ProjectNamedArchiveDownloadView.as_view(),
         name='project_named_archive_download_slug'),

    path('activity/', project_views.ProjectActivityView.as_view(), name='project_activity_slug'),

    path('sharing/', project_views.ProjectSharingView.as_view(), name='project_sharing_slug'),
    path('sharing/roles/', project_views.ProjectRoleUpdateView.as_view(), name='project_sharing_roles_slug'),
    path('settings/metadata/', project_views.ProjectSettingsMetadataView.as_view(),
         name='project_settings_metadata_slug'),
    path('settings/access/', project_views.ProjectSettingsAccessView.as_view(), name='project_settings_access_slug'),

    path('published/<slug:slug>/', project_views.PublishedView.as_view(), name='project_published_view_slug'),
    path('published/<slug:slug>/content/', project_views.PublishedContentView.as_view(),
         name='project_published_content_view_slug'),
    path('published/<slug:slug>/content/<path:media_path>', project_views.PublishedMediaView.as_view(),
         name='project_published_media_view_slug'),

    path('delete/', project_views.ProjectDeleteView.as_view(), name='project_delete_slug'),

    path('executa/', project_views.ProjectExecutaView.as_view(), name='project_executa_slug'),
]

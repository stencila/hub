"""Create some file sources for each project."""

from projects.project_models import Project
from projects.source_models import FileSource, GithubSource, GoogleDocsSource, UrlSource


def run(*args):
    """
    Create one of each source type in each project. The project name is
    used in the address attribute of each source so that we can try out filtering
    projects by searching for a particular source.
    """
    for project in Project.objects.all():
        FileSource.objects.create(
            project=project, path="file-source"
        )
        GithubSource.objects.create(
            project=project, path="github-source", repo="org/{}".format(project.name)
        )
        GoogleDocsSource.objects.create(
            project=project, path="google-docs-source", doc_id="gdoc-{}".format(project.name)
        )
        UrlSource.objects.create(
            project=project, path="url-source", url="http://example.org/{}".format(project.name)
        )

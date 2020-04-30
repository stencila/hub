from django.conf import settings
from django.core.management.base import BaseCommand
from django.http import HttpRequest

from projects.project_models import Project
from projects.project_puller import ProjectSourcePuller
from projects.source_models import LinkedSourceAuthentication


class Command(BaseCommand):
    help = "Pulls all FileSources for all projects."

    def handle(self, *args, **options):
        if not settings.STORAGE_DIR:
            raise RuntimeError(
                "STORAGE_DIR setting must be set to pull Project files."
            )

        request = HttpRequest()
        # django messages need a request to work with, although they are only used if there is an error with a
        # GitHubSource which we aren't working with so this stub object is OK

        lsa = LinkedSourceAuthentication(None)
        # Again, the Puller is not dealing with GitHubSources so it is OK if this is a stub

        for project in Project.objects.all():
            print("Pulling Project {}".format(project.id))
            puller = ProjectSourcePuller(
                project, settings.STORAGE_DIR, lsa, request
            )
            puller.pull(True)
            print("Finished pulling Project {}".format(project.id))

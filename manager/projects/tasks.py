from celery import shared_task

from projects.models.projects import Project
from projects.models.providers import GithubRepo
from users.models import User


@shared_task
def update_image_all_projects():
    """
    Update the image for all projects.

    Likely to be called on a regular basis e.g. daily
    by a periodic task.
    """
    Project.update_image_all_projects()


@shared_task
def update_image_for_project(project_id: int):
    """
    Update the image for a particular project.

    Likely to be called from the admin or when
    a project is updated.
    """
    project = Project.objects.get(id=project_id)
    project.update_image()


@shared_task
def refresh_github_repos_all_users():
    """
    Refresh list of GitHub repos for all users.

    Likely to be called on a regular basis e.g. daily
    by a periodic task.
    """
    GithubRepo.refresh_for_all_users()


@shared_task
def refresh_github_repos_for_user(user_id: int):
    """
    Refresh list of GitHub repos for a particular user.

    Likely to be called when a user signs in using GitHub
    or (re)connects their GitHub account.
    """
    user = User.objects.get(id=user_id)
    GithubRepo.refresh_for_user(user)

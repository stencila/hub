from celery import shared_task

from projects.models.providers import GithubRepo
from users.models import User


@shared_task
def update_github_repos_all_users():
    """
    Update list of GitHub repos for all users.

    Likely to be called on a regular basis e.g. daily
    by a periodic task.
    """
    GithubRepo.update_for_all_users()


@shared_task
def update_github_repos_for_user(user_id: int):
    """
    Update list of GitHub repos for a particular user.

    Likely to be called when a user signs in using GitHub
    or (re)connects their GitHub account.
    """
    user = User.objects.get(id=user_id)
    GithubRepo.update_for_user(user)

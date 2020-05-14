"""
Assign jobs to the test users (if any exist in the db).
"""
from datetime import datetime, timedelta
from random import randint, choice

from django.contrib.auth.models import User
from django.conf import settings

# from accounts.models import Account, AccountUserRole, AccountRole
from jobs.models import Job, JobMethod, JobStatus
from projects.models import Project


def run(*args):
    # Ensure that this is only used in development
    assert settings.DEBUG

    # Assumes that there are at least 3 projects
    projects = Project.objects.all()
    user = User.objects.all()
    now = datetime.now()
    creator = user[0]

    i = 0
    while i < 3:
        minutes = randint(0, 37)
        seconds = randint(0, 59)
        ended = now + timedelta(minutes=minutes, seconds=seconds)
        status = choice(list(JobStatus))
        method = choice(list(JobMethod))
        Job.objects.create(
            project=projects[randint(0, 2)],
            began=now,
            ended=ended,
            status=JobStatus[status],
            creator=creator,
            method=JobMethod[method],
        )
        # jobs.append(job)

    # for user in User.objects.all():
    # for account in Account.objects.all():
    #     if user not in account.get_administrators():
    #         AccountUserRole.objects.create(
    #             account=account,
    #             user=user,
    #             role=AccountRole.objects.order_by("?").first(),
    #         )

"""
Assign jobs to the test users (if any exist in the db).
"""
from datetime import datetime, timezone
from random import randint

from django.contrib.auth.models import User
from django.conf import settings

# from django.utils import timezone

from jobs.models import Job, JobMethod, JobStatus
from projects.models import Project


def run(*args):
    # Ensure that this is only used in development
    assert settings.DEBUG

    # Assumes that there are at least 3 projects
    projects = Project.objects.all()
    user = User.objects.all()
    now = datetime.now(timezone.utc)

    minutes = randint(0, 59) * 60 * 1000
    seconds = randint(0, 59) * 1000

    job1 = Job.objects.create(
        project=projects[randint(0, 2)],
        began=now,
        status=JobStatus.STARTED.value,
        creator=user[randint(0, len(user) - 1)],
        method=JobMethod.encode.value,
        log=[
            {
                "time": "2019-07-02T21:19:24.872Z",
                "level": 3,
                "message": """
                Nullam quis risus eget urna mollis ornare vel eu leo. Donec sed
                odio dui. Sed posuere consectetur est at lobortis. Vestibulum id
                ligula porta felis euismod semper. Praesent commodo cursus
                magna, vel scelerisque nisl consectetur et. Maecenas faucibus
                mollis interdum.""".strip(),
            },
            {
                "time": "2019-07-02T21:19:24.872Z",
                "level": 3,
                "message": """
                Vivamus sagittis lacus vel augue laoreet rutrum faucibus dolor
                auctor. Donec id elit non mi porta gravida at eget metus.
                """.strip(),
            },
        ],
        runtime=minutes + seconds,
    )

    minutes = randint(0, 37) * 60 * 1000
    seconds = randint(0, 59) * 1000

    job2 = Job.objects.create(
        project=projects[randint(0, 2)],
        began=now,
        status=JobStatus.FAILURE.value,
        creator=user[randint(0, len(user) - 1)],
        method=JobMethod.encode.value,
        log=[
            {
                "time": "2019-07-02T21:19:24.872Z",
                "level": 2,
                "message": """
                Aenean lacinia bibendum nulla sed consectetur. Cras justo odio,
                dapibus ac facilisis in, egestas eget quam. Nullam quis risus
                eget urna mollis ornare vel eu leo.
                """.strip(),
            }
        ],
        runtime=minutes + seconds,
    )

    for user in User.objects.all():
        job1.users.add(user)
        job2.users.add(user)

    job1.save()
    job2.save()

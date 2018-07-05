from django.contrib.auth.models import User
from director.models import Project


def run(*args):
    user=User.objects.all()[0]
    project = Project.objects.create(
        address='github://michael/documents/welcome-to-stencila',
        gallery=True, public=True,
        name='welcome-to-stencila',
        creator=user,
    )
    project.viewers.add(user)
